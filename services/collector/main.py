from __future__ import annotations

import json
import os
import random
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query
from jsonschema import Draft202012Validator
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from aegis_common.schema_mapper import MappingError, load_profiles, normalize_with_profile, profile_summaries
from aegis_common.time_utils import utc_now_iso
from aegis_common.topics import topic_for_event, TOPIC_VALIDATION_FAILED

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
SCHEMA_PATH = Path("/app/schemas/gameplay_event.schema.json")
PROFILE_DIR = Path(os.getenv("SOURCE_SCHEMA_DIR", "/app/source_schemas"))
DEFAULT_SOURCE_PROFILE = os.getenv("DEFAULT_SOURCE_PROFILE", "aegis_default")

ENABLE_LOAD_SHEDDING = os.getenv("ENABLE_LOAD_SHEDDING", "true").lower() == "true"
LOAD_SHED_BATCH_THRESHOLD = int(os.getenv("LOAD_SHED_BATCH_THRESHOLD", "750"))
PRIORITY2_SAMPLE_RATE = float(os.getenv("PRIORITY2_SAMPLE_RATE", "0.65"))
PRIORITY3_SAMPLE_RATE = float(os.getenv("PRIORITY3_SAMPLE_RATE", "0.10"))

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
validator = Draft202012Validator(schema)
profiles = load_profiles(PROFILE_DIR)

app = FastAPI(title="AegisTelemetry Collector", version="0.3.0")
producer: KafkaProducer | None = None
accepted_events = 0
failed_events = 0
sampled_or_dropped_events = 0
mapped_events = 0

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

def get_profile(profile_name: str):
    if profile_name not in profiles:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Unknown source profile '{profile_name}'",
                "available_profiles": sorted(profiles.keys()),
            },
        )
    return profiles[profile_name]

def normalize_payload_shape(payload: Any) -> tuple[str | None, list[dict[str, Any]]]:
    """Supports:
    - single event object
    - list of events
    - {"source_profile": "...", "event": {...}}
    - {"source_profile": "...", "events": [{...}, ...]}
    """
    if isinstance(payload, list):
        return None, payload

    if isinstance(payload, dict) and "events" in payload:
        events = payload.get("events")
        if not isinstance(events, list):
            raise HTTPException(status_code=400, detail="'events' must be a list")
        return payload.get("source_profile"), events

    if isinstance(payload, dict) and "event" in payload:
        event = payload.get("event")
        if not isinstance(event, dict):
            raise HTTPException(status_code=400, detail="'event' must be an object")
        return payload.get("source_profile"), [event]

    if isinstance(payload, dict):
        return payload.get("source_profile"), [payload]

    raise HTTPException(status_code=400, detail="Payload must be an event object, list, or wrapper with events")

def should_keep_event(event: dict[str, Any], batch_size: int) -> bool:
    if not ENABLE_LOAD_SHEDDING or batch_size < LOAD_SHED_BATCH_THRESHOLD:
        return True

    priority = int(event.get("priority") or 1)
    if priority <= 1:
        return True
    if priority == 2:
        return random.random() <= PRIORITY2_SAMPLE_RATE
    return random.random() <= PRIORITY3_SAMPLE_RATE

def emit_validation_failure(raw_event: dict[str, Any], canonical_event: dict[str, Any] | None, error_text: str) -> None:
    global failed_events
    failed_events += 1
    if producer is None:
        return

    event_for_id = canonical_event or raw_event
    producer.send(
        TOPIC_VALIDATION_FAILED,
        key=event_for_id.get("event_id", ""),
        value={
            "failed_at": utc_now_iso(),
            "event": canonical_event or raw_event,
            "raw_event": raw_event,
            "source_profile": (canonical_event or raw_event).get("source_profile"),
            "error": error_text,
        },
    )

def ingest_events(events: list[dict[str, Any]], source_profile: str) -> dict[str, Any]:
    global accepted_events, sampled_or_dropped_events, mapped_events

    if producer is None:
        raise HTTPException(status_code=503, detail="Producer not ready")

    profile = get_profile(source_profile)
    batch_size = len(events)
    results = {
        "source_profile": source_profile,
        "accepted": 0,
        "failed": 0,
        "sampled_or_dropped": 0,
        "mapped": 0,
        "validation_errors": [],
    }

    for raw_event in events:
        canonical_event: dict[str, Any] | None = None

        try:
            canonical_event = normalize_with_profile(raw_event, profile)
            mapped_events += 1
            results["mapped"] += 1
        except MappingError as exc:
            error_text = str(exc)
            emit_validation_failure(raw_event, None, error_text)
            results["failed"] += 1
            results["validation_errors"].append({"event_id": raw_event.get("event_id") or raw_event.get("id"), "error": error_text})
            continue

        canonical_event.setdefault("event_id", str(uuid.uuid4()))
        canonical_event.setdefault("ingest_time", utc_now_iso())
        canonical_event.setdefault("priority", 1)
        canonical_event.setdefault("category", "gameplay")

        if not should_keep_event(canonical_event, batch_size=batch_size):
            sampled_or_dropped_events += 1
            results["sampled_or_dropped"] += 1
            continue

        errors = sorted(validator.iter_errors(canonical_event), key=lambda e: e.path)
        if errors:
            error_text = "; ".join(error.message for error in errors[:5])
            emit_validation_failure(raw_event, canonical_event, error_text)
            results["failed"] += 1
            results["validation_errors"].append({"event_id": canonical_event.get("event_id"), "error": error_text})
            continue

        topic = topic_for_event(canonical_event)
        partition_key = canonical_event.get("server_id") or canonical_event.get("match_id") or canonical_event.get("region", "unknown")
        producer.send(topic, key=str(partition_key), value=canonical_event)
        accepted_events += 1
        results["accepted"] += 1

    producer.flush(timeout=2)
    return results

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
        "mapped_events": mapped_events,
        "sampled_or_dropped_events": sampled_or_dropped_events,
        "default_source_profile": DEFAULT_SOURCE_PROFILE,
        "available_source_profiles": sorted(profiles.keys()),
        "adaptive_sampling": {
            "enabled": ENABLE_LOAD_SHEDDING,
            "batch_threshold": LOAD_SHED_BATCH_THRESHOLD,
            "priority2_sample_rate": PRIORITY2_SAMPLE_RATE,
            "priority3_sample_rate": PRIORITY3_SAMPLE_RATE,
        },
    }

@app.get("/v1/source-profiles")
def list_source_profiles() -> dict[str, Any]:
    return {
        "default_source_profile": DEFAULT_SOURCE_PROFILE,
        "profiles": profile_summaries(profiles),
    }

@app.post("/v1/events")
def ingest(
    payload: Any = Body(...),
    source_profile: str | None = Query(default=None, description="Mapping profile used to normalize non-canonical telemetry"),
) -> dict[str, Any]:
    wrapper_profile, events = normalize_payload_shape(payload)
    chosen_profile = source_profile or wrapper_profile or DEFAULT_SOURCE_PROFILE
    return ingest_events(events, chosen_profile)

@app.post("/v1/events/{source_profile}")
def ingest_with_profile(source_profile: str, payload: Any = Body(...)) -> dict[str, Any]:
    _, events = normalize_payload_shape(payload)
    return ingest_events(events, source_profile)
