from __future__ import annotations

CANONICAL_REQUIRED_FIELDS = [
    "event_id",
    "event_time",
    "category",
    "event_type",
    "priority",
    "region",
    "server_id",
    "match_id",
    "map_id",
    "zone_id",
    "build_version",
]

CANONICAL_OPTIONAL_FIELDS = [
    "ingest_time",
    "player_count",
    "players_nearby",
    "ability_id",
    "cpu_percent",
    "memory_mb",
    "server_frame_ms",
    "packet_loss_percent",
    "packet_out_kbps",
    "desync_count",
    "rubberband_count",
    "replicated_objects",
    "physics_events",
    "ai_agents_active",
    "ai_pathfinding_requests",
    "matchmaking_queue_length",
    "sequence_id",
    "server_tick",
]

CANONICAL_DEFAULTS = {
    "category": "gameplay",
    "priority": 1,
    "build_version": "unknown",
    "player_count": 0,
    "players_nearby": 0,
    "ability_id": "",
    "cpu_percent": 0.0,
    "memory_mb": 0.0,
    "server_frame_ms": 0.0,
    "packet_loss_percent": 0.0,
    "packet_out_kbps": 0.0,
    "desync_count": 0,
    "rubberband_count": 0,
    "replicated_objects": 0,
    "physics_events": 0,
    "ai_agents_active": 0,
    "ai_pathfinding_requests": 0,
    "matchmaking_queue_length": 0,
}

CANONICAL_NUMERIC_FIELDS = {
    "priority": int,
    "player_count": int,
    "players_nearby": int,
    "cpu_percent": float,
    "memory_mb": float,
    "server_frame_ms": float,
    "packet_loss_percent": float,
    "packet_out_kbps": float,
    "desync_count": int,
    "rubberband_count": int,
    "replicated_objects": int,
    "physics_events": int,
    "ai_agents_active": int,
    "ai_pathfinding_requests": int,
    "matchmaking_queue_length": int,
    "sequence_id": int,
    "server_tick": int,
}

CANONICAL_FIELDS = CANONICAL_REQUIRED_FIELDS + CANONICAL_OPTIONAL_FIELDS
