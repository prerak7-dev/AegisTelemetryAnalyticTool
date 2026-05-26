# Server Selection Dashboard Upgrade

This upgrade adds a server explorer to the Streamlit dashboard.

## What changed

The dashboard now discovers available servers from `agg_zone_30s` and exposes:

- Region selector
- Server selector
- Analysis time-window selector
- Sidebar server inventory table
- Selected-server drilldown tab

## New views

### Command Center

Fleet or selected-server overview.

### Selected Server Analytics

Per-server drilldown with:

- Server frame time by zone
- Hot-zone risk by zone
- Active players
- AoE event volume
- Physics event volume
- Replicated object pressure
- Desync/rubberband impact
- Zone-level pressure source table

### Incident Deep Dive

Filtered by selected region/server.

### Data Quality

Filtered by selected region/server.

### Scaling Readiness

Shows recommended action by server, allowing a stakeholder to see which individual servers/shards are creating scaling pressure.

## Usage

1. Start the stack:

```bash
docker compose down -v
docker compose up --build
```

2. Generate traffic:

```bash
cd simulator
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 1000 --duration-sec 240
```

3. Open:

```text
http://localhost:8501
```

4. Use the sidebar:

- Select a region.
- Select a server.
- Inspect the selected server analytics tab.
