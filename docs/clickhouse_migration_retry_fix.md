# ClickHouse Migration Retry Fix

If `clickhouse-migrate` exits with code `210`, the migration container usually tried to connect before ClickHouse's native client port was ready, even though HTTP health already reported healthy.

This patch makes the migration service retry up to 60 times and makes the migration SQL safe for both:

- fresh databases
- existing local volumes from older phases

## Run

```bash
docker compose down
docker compose up --build
```

If the previous failed migration container is stuck, run:

```bash
docker compose down --remove-orphans
docker compose up --build
```

A clean reset is still valid for demos:

```bash
docker compose down -v
docker compose up --build
```
