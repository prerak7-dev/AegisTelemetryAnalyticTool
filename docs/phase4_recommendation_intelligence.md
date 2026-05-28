# Phase 4 — Recommendation Intelligence

Phase 4 replaces generic incident text with a richer issue taxonomy and recommendation engine.

## Issue types

- AoE replication overload
- Physics simulation spike
- Network packet pressure
- Local density tick-budget pressure
- AI pathfinding pressure
- Memory pressure / allocation churn
- Regional capacity / matchmaking surge
- Desync / hit-registration risk

Each incident now includes ranked issue candidates with owners, evidence, specific actions, investigation steps, validation plans, guardrail metrics, and tradeoffs.

## New aggregate signals

`agg_zone_30s` now includes packet-out, memory, AI, matchmaking, top ability, and top event-type fields.

Because the ClickHouse schema changed, reset local volumes:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

## New scenario examples

```bash
python generate_traffic.py --scenario ai_pathfinding_spike --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
python generate_traffic.py --scenario memory_pressure --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
python generate_traffic.py --scenario network_packet_pressure --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
```
