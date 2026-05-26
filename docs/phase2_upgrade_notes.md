# Phase 2 Upgrade Notes

Phase 2 turns the MVP into a more credible senior analytics portfolio tool.

## Added capabilities

1. Incident attribution scoring
   - Ranks likely drivers instead of returning one hard-coded cause.
   - Distinguishes AoE/replication, physics spikes, player density, and network pressure.
   - Stores ranked driver scores in the incident evidence payload.

2. Data quality failure path
   - Invalid events are sent to `telemetry.validation.failed`.
   - Processor stores failures in ClickHouse.
   - Dashboard includes a Data Quality tab.

3. Adaptive telemetry sampling
   - Collector preserves priority 0/1 events.
   - Priority 2 events are sampled during high-volume batches.
   - Priority 3 events are dropped first during pressure.
   - Collector `/health` exposes sampling configuration and counters.

4. Stronger synthetic incident topology
   - Weekend Event Meltdown now uses stable affected servers and zones.
   - Aggregates accumulate enough evidence for cleaner incident cards.

5. Dashboard tabs
   - Command Center
   - Incident Deep Dive
   - Data Quality
   - Scaling Readiness

## Reset required

Because Phase 2 adds a new ClickHouse table, reset the local volume:

```bash
docker compose down -v
docker compose up --build
```

## Phase 2 demo commands

Normal traffic:

```bash
python generate_traffic.py --scenario normal_load --collector-url http://localhost:8000 --events-per-second 300 --duration-sec 90
```

Meltdown traffic:

```bash
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 1000 --duration-sec 240
```

Data-quality demo:

```bash
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120 --invalid-rate 0.02
```
