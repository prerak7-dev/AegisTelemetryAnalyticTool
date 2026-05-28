# ClickHouse Migration Fix

If the dashboard reports:

```text
Unknown expression identifier 'source_profile'
```

then ClickHouse is still using a table created before Phase 3.1 added `source_profile`.

This patch adds a `clickhouse-migrate` service to `docker-compose.yml`. It runs:

```sql
ALTER TABLE ... ADD COLUMN IF NOT EXISTS source_profile ...
```

for:

- `raw_events`
- `agg_zone_30s`
- `incidents`
- `data_quality_failures`

## Run

```bash
docker compose down
docker compose up --build
```

You do not need `-v` for this migration patch. Existing local data is preserved and older rows receive the default source profile `legacy_unknown`.

If you want a totally clean local demo database, you can still run:

```bash
docker compose down -v
docker compose up --build
```
