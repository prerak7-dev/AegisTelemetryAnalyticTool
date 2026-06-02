# Deployment and Runtime

## Local development

```bash
docker compose down --remove-orphans
docker compose up --build
```

Services:

```text
redpanda
redpanda-console
clickhouse
collector
processor
dashboard
```

Ports:

| Service | URL |
|---|---|
| Dashboard | `http://localhost:8501` |
| Collector | `http://localhost:8000` |
| Redpanda Console | `http://localhost:8080` |
| ClickHouse HTTP | `http://localhost:8123` |

## Mounted directories

Dashboard mounts:

```text
config -> /app/config
simulator -> /app/simulator
sql -> /app/sql
notebooks -> /app/notebooks
docs -> /app/docs
data -> /app/data
```

This allows editing configs, scenarios, docs, SQL, and notebooks without rebuilding.

## Important environment variables

```text
CLICKHOUSE_HOST
CLICKHOUSE_PORT
CLICKHOUSE_DATABASE
CLICKHOUSE_PASSWORD
AEGIS_DASHBOARD_PERFORMANCE_CONFIG
KAFKA_BOOTSTRAP_SERVERS
WINDOW_GRACE_SECONDS
RECOMMENDATION_RULE_DIR
TIMELINE_STAGE_DIR
```

## Resetting local data

The Demo Control Center can reset configured demo tables.

For a hard reset:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

This removes Docker volumes, including ClickHouse data.
