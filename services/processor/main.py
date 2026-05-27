from __future__ import annotations

import json
import os
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any

import clickhouse_connect
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable

from aegis_common.recommendation_engine import evaluate_issues, top_issue
from aegis_common.stats import quantile, risk_score
from aegis_common.time_utils import parse_time, floor_window
from aegis_common.topics import PROCESSOR_TOPICS, TOPIC_INCIDENTS, TOPIC_VALIDATION_FAILED

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "aegis_telemetry")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "aegis_dev_password")
PROCESSOR_GROUP_ID = os.getenv("PROCESSOR_GROUP_ID", "aegis-processor-local")
WINDOW_SECONDS = 30
WINDOW_GRACE_SECONDS = int(os.getenv("WINDOW_GRACE_SECONDS", "8"))

@dataclass
class WindowState:
    window_start: datetime
    window_end: datetime
    source_profile: str
    region: str
    server_id: str
    map_id: str
    zone_id: str
    build_version: str
    events: int = 0
    player_counts: list[int] = field(default_factory=list)
    ability_casts: int = 0
    aoe_events: int = 0
    physics_event_count: int = 0
    replicated_objects: list[float] = field(default_factory=list)
    cpu_values: list[float] = field(default_factory=list)
    memory_values: list[float] = field(default_factory=list)
    server_frame_values: list[float] = field(default_factory=list)
    packet_loss_values: list[float] = field(default_factory=list)
    packet_out_values: list[float] = field(default_factory=list)
    ai_agents_active_values: list[float] = field(default_factory=list)
    ai_pathfinding_requests: int = 0
    matchmaking_events: int = 0
    matchmaking_queue_values: list[float] = field(default_factory=list)
    desync_events: int = 0
    rubberband_events: int = 0
    ability_counter: Counter = field(default_factory=Counter)
    event_type_counter: Counter = field(default_factory=Counter)

    def update(self, event: dict[str, Any]) -> None:
        event_type = event.get("event_type", "")
        ability_id = event.get("ability_id", "")
        self.events += 1
        self.event_type_counter[event_type] += 1
        if ability_id:
            self.ability_counter[ability_id] += 1
        self.player_counts.append(int(event.get("players_nearby") or event.get("player_count") or 0))
        if event_type in {"ability_cast", "aoe_ability_cast"}:
            self.ability_casts += 1
        if event_type == "aoe_ability_cast" or str(ability_id).startswith("aoe_"):
            self.aoe_events += 1
        if event_type in {"session_started", "matchmaking_event"} or event.get("category") == "matchmaking":
            self.matchmaking_events += 1
        self.physics_event_count += int(event.get("physics_events") or (1 if event_type == "physics_event" else 0))
        self.replicated_objects.append(float(event.get("replicated_objects") or 0))
        self.cpu_values.append(float(event.get("cpu_percent") or 0))
        self.memory_values.append(float(event.get("memory_mb") or 0))
        self.server_frame_values.append(float(event.get("server_frame_ms") or 0))
        self.packet_loss_values.append(float(event.get("packet_loss_percent") or 0))
        self.packet_out_values.append(float(event.get("packet_out_kbps") or 0))
        self.ai_agents_active_values.append(float(event.get("ai_agents_active") or 0))
        self.ai_pathfinding_requests += int(event.get("ai_pathfinding_requests") or (1 if event_type == "ai_pathfinding_request" else 0))
        self.matchmaking_queue_values.append(float(event.get("matchmaking_queue_length") or 0))
        self.desync_events += int(event.get("desync_count") or (1 if event_type == "desync_detected" else 0))
        self.rubberband_events += int(event.get("rubberband_count") or (1 if event_type == "rubberband_detected" else 0))

    def _top(self, counter: Counter) -> str:
        return str(counter.most_common(1)[0][0]) if counter else ""

    def metrics(self) -> dict[str, Any]:
        active_players = max(self.player_counts) if self.player_counts else 0
        return {
            "active_players": active_players,
            "p95_frame": quantile(self.server_frame_values, 0.95),
            "p99_frame": quantile(self.server_frame_values, 0.99),
            "avg_frame": sum(self.server_frame_values) / len(self.server_frame_values) if self.server_frame_values else 0.0,
            "cpu_p95": quantile(self.cpu_values, 0.95),
            "memory_p95": quantile(self.memory_values, 0.95),
            "packet_loss_p95": quantile(self.packet_loss_values, 0.95),
            "packet_out_p95": quantile(self.packet_out_values, 0.95),
            "replicated_p95": quantile(self.replicated_objects, 0.95),
            "ai_agents_active_p95": quantile(self.ai_agents_active_values, 0.95),
            "ai_pathfinding_requests": self.ai_pathfinding_requests,
            "matchmaking_events": self.matchmaking_events,
            "matchmaking_queue_p95": quantile(self.matchmaking_queue_values, 0.95),
            "aoe_events": self.aoe_events,
            "physics_events": self.physics_event_count,
            "desync_events": self.desync_events,
            "rubberband_events": self.rubberband_events,
            "top_ability_id": self._top(self.ability_counter),
            "top_event_type": self._top(self.event_type_counter),
        }

    def hot_risk(self) -> float:
        m = self.metrics()
        return risk_score(
            players=int(m["active_players"]),
            server_frame_p95=float(m["p95_frame"]),
            cpu_p95=float(m["cpu_p95"]),
            packet_loss_p95=float(m["packet_loss_p95"]),
            desync_events=self.desync_events,
            rubberband_events=self.rubberband_events,
            aoe_events=self.aoe_events,
            replicated_objects_p95=float(m["replicated_p95"]),
        )

    def to_row(self) -> tuple:
        m = self.metrics()
        return (
            self.window_start, self.window_end, self.source_profile, self.region, self.server_id, self.map_id,
            self.zone_id, self.build_version, self.events, int(m["active_players"]), self.ability_casts,
            self.aoe_events, self.physics_event_count, float(m["replicated_p95"]), float(m["cpu_p95"]),
            float(m["avg_frame"]), float(m["p95_frame"]), float(m["p99_frame"]), float(m["packet_loss_p95"]),
            float(m["packet_out_p95"]), float(m["memory_p95"]), float(m["ai_agents_active_p95"]),
            int(m["ai_pathfinding_requests"]), int(m["matchmaking_events"]), float(m["matchmaking_queue_p95"]),
            str(m["top_ability_id"]), str(m["top_event_type"]), self.desync_events, self.rubberband_events,
            self.hot_risk(),
        )

    def incident(self) -> dict[str, Any] | None:
        m = self.metrics()
        hot_risk = self.hot_risk()
        issues = evaluate_issues(m)
        top = top_issue(m)
        should_emit = (
            hot_risk >= 55 or float(m["p95_frame"]) >= 50 or float(m["packet_loss_p95"]) >= 5
            or int(m["ai_pathfinding_requests"]) >= 300 or float(m["memory_p95"]) >= 8500
            or int(m["matchmaking_events"]) >= 250 or int(m["desync_events"]) + int(m["rubberband_events"]) >= 25
        )
        if not should_emit:
            return None
        severity = "critical" if hot_risk >= 80 or float(m["p99_frame"]) >= 80 or top["score"] >= 0.75 else "warning"
        recommended_actions = top.get("recommended_actions", [])
        recommended_action = " ".join(recommended_actions[:2]) if recommended_actions else "Open the incident evidence and investigate the highest-scoring driver."
        evidence = {
            "source_profile": self.source_profile,
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "active_players": int(m["active_players"]),
            "top_ability_id": m["top_ability_id"],
            "top_event_type": m["top_event_type"],
            "aoe_events": self.aoe_events,
            "physics_events": self.physics_event_count,
            "replicated_objects_p95": float(m["replicated_p95"]),
            "cpu_p95": float(m["cpu_p95"]),
            "memory_p95": float(m["memory_p95"]),
            "packet_loss_p95": float(m["packet_loss_p95"]),
            "packet_out_kbps_p95": float(m["packet_out_p95"]),
            "ai_agents_active_p95": float(m["ai_agents_active_p95"]),
            "ai_pathfinding_requests": int(m["ai_pathfinding_requests"]),
            "matchmaking_events": int(m["matchmaking_events"]),
            "matchmaking_queue_p95": float(m["matchmaking_queue_p95"]),
            "desync_events": self.desync_events,
            "rubberband_events": self.rubberband_events,
            "hot_zone_risk_score": hot_risk,
            "issue_candidates": issues,
        }
        return {
            "detected_at": datetime.now(timezone.utc),
            "incident_id": f"inc_{uuid.uuid4().hex[:12]}",
            "severity": severity,
            "source_profile": self.source_profile,
            "region": self.region,
            "server_id": self.server_id,
            "map_id": self.map_id,
            "zone_id": self.zone_id,
            "build_version": self.build_version,
            "symptom": f"{top['title']} · p95 frame {float(m['p95_frame']):.1f} ms · p99 {float(m['p99_frame']):.1f} ms · risk {hot_risk:.1f}",
            "likely_driver": top["issue_type"],
            "confidence": float(top["confidence"]),
            "player_impact": top["impact"],
            "recommended_action": recommended_action,
            "evidence_json": json.dumps(evidence),
        }

def wait_for_consumer() -> KafkaConsumer:
    for _ in range(30):
        try:
            return KafkaConsumer(
                *PROCESSOR_TOPICS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=PROCESSOR_GROUP_ID,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
                key_deserializer=lambda b: b.decode("utf-8") if b else None,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
            )
        except NoBrokersAvailable:
            time.sleep(2)
    raise RuntimeError("Kafka broker unavailable after retries")

def wait_for_producer() -> KafkaProducer:
    for _ in range(30):
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda v: v.encode("utf-8") if isinstance(v, str) else v,
                acks="all",
                retries=5,
            )
        except NoBrokersAvailable:
            time.sleep(2)
    raise RuntimeError("Kafka broker unavailable after retries")

def clickhouse_client():
    for _ in range(30):
        try:
            client = clickhouse_connect.get_client(
                host=CLICKHOUSE_HOST,
                port=CLICKHOUSE_PORT,
                database=CLICKHOUSE_DATABASE,
                username="default",
                password=CLICKHOUSE_PASSWORD,
            )
            client.command("SELECT 1")
            return client
        except Exception as exc:
            print(f"Waiting for ClickHouse: {exc}")
            time.sleep(2)
    raise RuntimeError("ClickHouse unavailable after retries")

def raw_event_row(event: dict[str, Any]) -> tuple:
    event_time = parse_time(event["event_time"])
    ingest_time = parse_time(event.get("ingest_time") or event["event_time"])
    return (
        event_time, ingest_time, event.get("event_id", ""), event.get("category", ""), event.get("event_type", ""),
        event.get("source_profile", "unknown"), int(event.get("priority") or 1), event.get("region", ""),
        event.get("server_id", ""), event.get("match_id", ""), event.get("map_id", ""), event.get("zone_id", ""),
        event.get("build_version", ""), int(event.get("player_count") or 0), int(event.get("players_nearby") or 0),
        event.get("ability_id", ""), float(event.get("cpu_percent") or 0), float(event.get("memory_mb") or 0),
        float(event.get("server_frame_ms") or 0), float(event.get("packet_loss_percent") or 0),
        float(event.get("packet_out_kbps") or 0), int(event.get("desync_count") or 0),
        int(event.get("rubberband_count") or 0), int(event.get("replicated_objects") or 0),
        int(event.get("physics_events") or 0), json.dumps(event),
    )

def quality_failure_row(payload: dict[str, Any]) -> tuple:
    event = payload.get("event", {}) or {}
    failed_at_raw = payload.get("failed_at")
    try:
        failed_at = parse_time(failed_at_raw) if failed_at_raw else datetime.now(timezone.utc)
    except Exception:
        failed_at = datetime.now(timezone.utc)
    return (
        failed_at, event.get("event_id", ""), payload.get("error", "unknown validation error"),
        event.get("category", "unknown"), event.get("event_type", "unknown"),
        payload.get("source_profile") or event.get("source_profile", "unknown"),
        event.get("region", "unknown"), event.get("server_id", "unknown"), json.dumps(payload),
    )

def main() -> None:
    print("Starting AegisTelemetry realtime processor")
    consumer = wait_for_consumer()
    producer = wait_for_producer()
    ch = clickhouse_client()
    windows: dict[tuple, WindowState] = {}
    raw_buffer: list[tuple] = []
    quality_buffer: list[tuple] = []
    last_flush = time.time()
    while True:
        messages = consumer.poll(timeout_ms=1000, max_records=2000)
        for topic_partition, records in messages.items():
            for record in records:
                if record.topic == TOPIC_VALIDATION_FAILED:
                    quality_buffer.append(quality_failure_row(record.value))
                    continue
                event = record.value
                try:
                    event_time = parse_time(event["event_time"])
                except Exception:
                    continue
                raw_buffer.append(raw_event_row(event))
                window_start = floor_window(event_time, WINDOW_SECONDS)
                window_end = window_start + timedelta(seconds=WINDOW_SECONDS)
                key = (
                    window_start, event.get("source_profile", "unknown"), event.get("region", "unknown"),
                    event.get("server_id", "unknown"), event.get("map_id", "unknown"), event.get("zone_id", "unknown"),
                    event.get("build_version", "unknown"),
                )
                if key not in windows:
                    windows[key] = WindowState(window_start, window_end, key[1], key[2], key[3], key[4], key[5], key[6])
                windows[key].update(event)
        now = datetime.now(timezone.utc)
        should_flush = len(raw_buffer) >= 1000 or len(quality_buffer) >= 100 or time.time() - last_flush >= 3
        if should_flush:
            if raw_buffer:
                ch.insert("raw_events", raw_buffer, column_names=[
                    "event_time", "ingest_time", "event_id", "category", "event_type", "source_profile", "priority",
                    "region", "server_id", "match_id", "map_id", "zone_id", "build_version", "player_count",
                    "players_nearby", "ability_id", "cpu_percent", "memory_mb", "server_frame_ms", "packet_loss_percent",
                    "packet_out_kbps", "desync_count", "rubberband_count", "replicated_objects", "physics_events", "raw_json"
                ])
                raw_buffer.clear()
            if quality_buffer:
                ch.insert("data_quality_failures", quality_buffer, column_names=[
                    "failed_at", "event_id", "error", "category", "event_type", "source_profile", "region", "server_id", "raw_json"
                ])
                quality_buffer.clear()
            flushable_keys = [key for key, state in windows.items() if state.window_end + timedelta(seconds=WINDOW_GRACE_SECONDS) <= now]
            agg_rows = []
            incident_rows = []
            for key in flushable_keys:
                state = windows.pop(key)
                agg_rows.append(state.to_row())
                inc = state.incident()
                if inc:
                    incident_rows.append((
                        inc["detected_at"], inc["incident_id"], inc["severity"], inc["source_profile"], inc["region"],
                        inc["server_id"], inc["map_id"], inc["zone_id"], inc["build_version"], inc["symptom"],
                        inc["likely_driver"], inc["confidence"], inc["player_impact"], inc["recommended_action"], inc["evidence_json"]
                    ))
                    producer.send(TOPIC_INCIDENTS, key=inc["incident_id"], value=inc)
            if agg_rows:
                ch.insert("agg_zone_30s", agg_rows, column_names=[
                    "window_start", "window_end", "source_profile", "region", "server_id", "map_id", "zone_id",
                    "build_version", "events", "active_players", "ability_casts", "aoe_events", "physics_events",
                    "replicated_objects_p95", "cpu_p95", "server_frame_ms_avg", "server_frame_ms_p95", "server_frame_ms_p99",
                    "packet_loss_p95", "packet_out_kbps_p95", "memory_mb_p95", "ai_agents_active_p95",
                    "ai_pathfinding_requests", "matchmaking_events", "matchmaking_queue_p95", "top_ability_id", "top_event_type",
                    "desync_events", "rubberband_events", "hot_zone_risk_score"
                ])
            if incident_rows:
                ch.insert("incidents", incident_rows, column_names=[
                    "detected_at", "incident_id", "severity", "source_profile", "region", "server_id", "map_id", "zone_id",
                    "build_version", "symptom", "likely_driver", "confidence", "player_impact", "recommended_action", "evidence_json"
                ])
                producer.flush(timeout=2)
            last_flush = time.time()
            print(f"flushed agg={len(agg_rows)} incidents={len(incident_rows)} open_windows={len(windows)}")

if __name__ == "__main__":
    main()
