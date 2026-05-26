from __future__ import annotations

import json
import os
import random
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from jsonschema import Draft202012Validator
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from aegis_common.time_utils import utc_now_iso
from aegis_common.topics import topic_for_event, TOPIC_VALIDATION_FAILED

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
SCHEMA_PATH = Path("/app/schemas/gameplay_event.schema.json")

ENABLE_LOAD_SHEDDING = os.getenv("ENABLE_LOAD_SHEDDING", "true").lower() == "true"
LOAD_SHED_BATCH_THRESHOLD = int(os.getenv("LOAD_SHED_BATCH_THRESHOLD", "750"))
PRIORITY2_SAMPLE_RATE = float(os.getenv("PRIORITY2_SAMPLE_RATE", "0.65"))
PRIORITY3_SAMPLE_RATE = float(os.getenv("PRIORITY3_SAMPLE_RATE", "0.10"))

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
validator = Draft202012Validator(schema)

app = FastAPI(title="AegisTelemetry Collector", version="0.2.0")
producer: KafkaProducer | None = None
accepted_events = 0
failed_events = 0
sampled_or_dropped_events = 0

def make_producer() -> KafkaProducer:
    for _ in range(30):
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
                linger_ms=10,
                batch_size=64 * 1024,
                acks="all",
                retries=5,
            )
        except NoBrokersAvailable:
            time.sleep(2)
    raise RuntimeError("Kafka broker unavailable after retries")

def should_keep_event(event: dict[str, Any], batch_size: int) -> bool:
    """Priority-aware adaptive sampling.

    This protects game/collector pressure by preserving critical events and
    reducing low-value telemetry first when batch volume is high.
    """
    if not ENABLE_LOAD_SHEDDING or batch_size < LOAD_SHED_BATCH_THRESHOLD:
        return True

    priority = int(event.get("priority") or 1)

    # Priority 0 and 1 are preserved.
    if priority <= 1:
        return True

    if priority == 2:
        return random.random() <= PRIORITY2_SAMPLE_RATE

    # Priority 3/debug/cosmetic telemetry is dropped first under pressure.
    return random.random() <= PRIORITY3_SAMPLE_RATE

@app.on_event("startup")
def startup() -> None:
    global producer
    producer = make_producer()

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "kafka_bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
        "accepted_events": accepted_events,
        "failed_events": failed_events,
        "sampled_or_dropped_events": sampled_or_dropped_events,
        "adaptive_sampling": {
            "enabled": ENABLE_LOAD_SHEDDING,
            "batch_threshold": LOAD_SHED_BATCH_THRESHOLD,
            "priority2_sample_rate": PRIORITY2_SAMPLE_RATE,
            "priority3_sample_rate": PRIORITY3_SAMPLE_RATE,
        },
    }

@app.post("/v1/events")
def ingest(payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    global accepted_events, failed_events, sampled_or_dropped_events

    if producer is None:
        raise HTTPException(status_code=503, detail="Producer not ready")

    events = payload if isinstance(payload, list) else [payload]
    batch_size = len(events)
    results = {"accepted": 0, "failed": 0, "sampled_or_dropped": 0, "validation_errors": []}

    for event in events:
        event.setdefault("event_id", str(uuid.uuid4()))
        event.setdefault("ingest_time", utc_now_iso())
        event.setdefault("priority", 1)
        event.setdefault("category", "gameplay")

        if not should_keep_event(event, batch_size=batch_size):
            sampled_or_dropped_events += 1
            results["sampled_or_dropped"] += 1
            continue

        errors = sorted(validator.iter_errors(event), key=lambda e: e.path)
        if errors:
            failed_events += 1
            results["failed"] += 1
            error_text = "; ".join(error.message for error in errors[:5])
            results["validation_errors"].append({"event_id": event.get("event_id"), "error": error_text})
            producer.send(
                TOPIC_VALIDATION_FAILED,
                key=event.get("event_id", ""),
                value={
                    "failed_at": utc_now_iso(),
                    "event": event,
                    "error": error_text,
                },
            )
            continue

        topic = topic_for_event(event)
        partition_key = event.get("server_id") or event.get("match_id") or event.get("region", "unknown")
        producer.send(topic, key=str(partition_key), value=event)
        accepted_events += 1
        results["accepted"] += 1

    producer.flush(timeout=2)
    return results
