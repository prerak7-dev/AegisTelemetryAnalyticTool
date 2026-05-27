# Phase 3 — Schema Adaptability

Phase 3 adds a source-schema adapter layer.

## Why this matters

Real studios rarely hand analysts perfectly shaped data. Different teams, games, engines, services, and vendors often use different event names and field layouts.

A production-grade analytics tool should separate:

```text
raw source telemetry
        ↓
source-specific mapping profile
        ↓
canonical analytics event
        ↓
validation
        ↓
streaming / storage / dashboard
```

## New capabilities

### Source profiles

Profiles live in:

```text
source_schemas/
  aegis_default.json
  generic_live_service.json
  unreal_multiplayer.json
```

Each profile defines:

- source field paths
- canonical field destinations
- default values
- event type mappings
- category/value mappings

### New collector endpoints

List profiles:

```bash
curl http://localhost:8000/v1/source-profiles
```

Native canonical event ingestion:

```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -d @canonical_event.json
```

Profile-specific ingestion:

```bash
curl -X POST http://localhost:8000/v1/events/generic_live_service \
  -H "Content-Type: application/json" \
  -d @generic_events.json
```

Wrapper ingestion:

```json
{
  "source_profile": "generic_live_service",
  "events": [
    {
      "id": "abc",
      "ts": "2026-05-27T18:00:00Z",
      "regionName": "EU-West",
      "shardId": "eu-west-001"
    }
  ]
}
```

### Traceability

Canonical events include:

```json
{
  "source_profile": "generic_live_service",
  "source_event_raw": {
    "...": "original event payload"
  }
}
```

This lets analysts debug mapping issues and verify data lineage.

## Demo commands

Native Aegis schema:

```bash
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120
```

Generic live-service schema:

```bash
python generate_generic_traffic.py --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120
```

Unreal-style schema:

```bash
python generate_unreal_traffic.py --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120
```

## Dashboard

The dashboard now includes a `Source Schemas` workspace showing:

- supported mapping profiles
- profile descriptions
- observed source profiles in raw telemetry
- example ingestion commands
