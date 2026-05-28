# Phase 3.1 — Source Profile Filtering

This patch makes `source_profile` a first-class analytics dimension.

## What changed

`source_profile` is now included in:

- `raw_events`
- `agg_zone_30s`
- `incidents`
- `data_quality_failures`

The dashboard now supports:

- Source profile selector
- Source-aware server inventory
- Source-aware Command Center
- Source-aware Selected Server drilldown
- Source-aware Incident Dossier
- Source-aware Data Quality
- Source-aware Scaling Readiness
- Source-aware Source Schemas workspace

## Why this matters

If multiple traffic/schema sources are running at the same time, the platform can now separate:

- `aegis_default`
- `generic_live_service`
- `unreal_multiplayer`

This prevents mixed-source analytics from being ambiguous and lets the analyst compare how different telemetry producers normalize into the canonical model.

## Upgrade note

Because this patch changes ClickHouse table schemas, reset local volumes:

```bash
docker compose down -v
docker compose up --build
```

## Demo

Run all three traffic generators in separate terminals:

```bash
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
```

```bash
python generate_generic_traffic.py --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
```

```bash
python generate_unreal_traffic.py --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
```

Then open the dashboard and use:

```text
Source profile → All source profiles / aegis_default / generic_live_service / unreal_multiplayer
```
