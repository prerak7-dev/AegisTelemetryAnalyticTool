# Demo Script — Weekend Event Meltdown

## Goal

Show that AegisTelemetry can ingest realtime gameplay telemetry, detect a hot-zone server performance incident, explain likely drivers, and recommend optimization actions.

## Flow

1. Start the local stack.

```bash
docker compose up --build
```

2. Open dashboard.

```text
http://localhost:8501
```

3. Generate normal traffic.

```bash
cd simulator
python generate_traffic.py --scenario normal_load --collector-url http://localhost:8000 --events-per-second 300 --duration-sec 90
```

4. Generate meltdown traffic.

```bash
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 1000 --duration-sec 240
```

5. Narrate:

- EU-West / NA-East traffic rises.
- Northern Ridge becomes a high-risk hot zone.
- AoE ability density increases.
- Replicated object count increases.
- p95/p99 server frame time crosses threshold.
- Incidents appear with likely driver and recommendation.

## Stakeholder-facing conclusion

AegisTelemetry identified that the degradation was not simply caused by player count. The strongest signal was AoE event density combined with replicated object volume in a high-density zone. Recommended next action: reduce temporary AoE replication radius or update frequency above a player-density threshold, then validate with guardrail metrics for desync and hit registration.
