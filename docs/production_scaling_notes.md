# Production Scaling Notes

## Traffic-heavy game constraints

Telemetry must not harm the game server. The SDK should be async, buffered, batched, compressed, and priority-aware.

## Hot / warm / cold paths

### Hot path

- Seconds-level incident detection.
- Stream processing over rolling windows.
- Critical alerts continue even if dashboard/warehouse is degraded.

### Warm path

- Real-time dashboard.
- ClickHouse aggregate tables.
- Recent incidents and drilldowns.

### Cold path

- Parquet/data lake.
- Experiment readouts.
- Deep attribution notebooks.
- Build-over-build regression analysis.

## Topic strategy

- `gameplay.events.raw`
- `server.metrics.raw`
- `network.metrics.raw`
- `matchmaking.events.raw`
- `analytics.incidents.detected`
- `telemetry.validation.failed`

## Partition keys

- Server metrics: `server_id`
- Combat events: `match_id`
- Position samples: `region|map_id|zone_id`
- Matchmaking events: `region`

## Backpressure behavior

When collector queue depth or server CPU is high:

1. Preserve priority 0 events.
2. Aggregate priority 1 events.
3. Sample priority 2 events.
4. Drop priority 3 events.

## SLO examples

- Critical event ingestion p95 < 5 seconds.
- Incident detection p95 < 10 seconds.
- Dashboard freshness p95 < 30 seconds.
- Critical event loss < 0.1%.
