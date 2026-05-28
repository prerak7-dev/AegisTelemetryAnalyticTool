# AegisTelemetry — Real-Time Gameplay Performance Intelligence

A production-style portfolio project for analyzing high-volume gameplay telemetry, detecting realtime server-performance incidents, and generating evidence-backed optimization recommendations for AAA live-service games.

## Core agenda

This tool answers:

1. Where is server performance degrading right now?
2. Which gameplay behaviors are correlated with the degradation?
3. Is the issue caused by crowding, combat events, physics, object replication, network pressure, or scaling pressure?
4. What optimization should engineers/designers test next?

The MVP includes:

- Synthetic gameplay/server/network telemetry generator.
- FastAPI regional telemetry collector.
- Redpanda Kafka-compatible realtime event stream.
- Python stream processor with rolling-window aggregation.
- ClickHouse realtime analytical storage.
- Incident detector for hot zones, server hitches, network degradation, and scaling risk.
- Streamlit dashboard shell.
- Event schemas, data quality rules, and production scaling notes.

## Local architecture

```text
Synthetic game/server simulator
        ↓
FastAPI telemetry collector
        ↓
Redpanda topics
        ↓
Realtime processor
        ↓
ClickHouse raw + aggregate tables
        ↓
Streamlit dashboard
```

## Quick start

Requirements:

- Docker Desktop
- Python 3.11+ only if running simulator outside Docker

Start the stack:

```bash
docker compose up --build
```

Open:

```text
Collector health: http://localhost:8000/health
Streamlit dashboard: http://localhost:8501
Redpanda Console: http://localhost:8080
ClickHouse HTTP: http://localhost:8123
```

Generate traffic from your host machine:

```bash
cd simulator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 180
```

Linux/macOS activation:

```bash
source .venv/bin/activate
```

## Scenarios

- `normal_load`
- `weekend_event_meltdown`
- `physics_spike`
- `region_login_surge`
- `replication_overload`

Most important demo:

```bash
python generate_traffic.py --scenario weekend_event_meltdown --events-per-second 1000 --duration-sec 300
```

## Production scaling story

The local version is intentionally small enough to run on a laptop. The architecture is designed around high-traffic live-service constraints:

- Regional collectors
- Kafka-compatible partitioned event streams
- Priority-aware telemetry
- Hot/warm/cold data paths
- Rolling-window stream aggregation
- ClickHouse realtime OLAP
- Incident recommendations with evidence and confidence
- Backpressure and adaptive sampling design
- Production upgrade path to Kubernetes, Flink/Kafka Streams, ClickHouse clusters, object storage, and Prometheus/Grafana SLOs


## ClickHouse auth reset

If you see `AUTHENTICATION_FAILED` from the processor or dashboard, reset the local ClickHouse volume because credentials are persisted after the first initialization:

```bash
docker compose down -v
docker compose up --build
```

This MVP uses the local development password:

```text
CLICKHOUSE_PASSWORD=aegis_dev_password
```

Do not use this password in production.


## Phase 2 features

This version adds:

- Incident attribution scoring with ranked likely drivers.
- Data-quality failure stream and dashboard tab.
- Adaptive collector sampling under high-volume batches.
- More stable high-traffic scenario topology.
- Dashboard tabs for command center, incident deep dive, data quality, and scaling readiness.

Because this version adds a new ClickHouse table, reset local volumes when upgrading:

```bash
docker compose down -v
docker compose up --build
```

Optional data-quality demo:

```bash
cd simulator
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120 --invalid-rate 0.02
```


## Server selection dashboard

The dashboard now includes a server explorer. After generating realtime traffic, use the sidebar to select:

- Region
- Server
- Analysis time window

The dashboard filters Command Center, Incident Deep Dive, Data Quality, and Scaling Readiness views to the selected server. A dedicated `Selected Server Analytics` tab shows per-zone frame pressure, hot-zone risk, and likely pressure sources for that server.


## Phase 2.5 performance and design polish

This version improves dashboard responsiveness and presentation quality.

Performance changes:

- Replaced Streamlit tabs with a folder-style workspace selector so only one view renders at a time.
- Added short-TTL ClickHouse query caching.
- Live refresh is off by default.
- Added manual `Refresh now`.
- Added refresh interval selector.
- Added table row limit.
- Bounded large queries with selected time window and SQL limits.

Design changes:

- Premium dark operations-dossier look.
- Folder/paper-inspired workspace navigation.
- Paper-style metric cards.
- Dark red/gold accents.
- More polished portfolio-ready dashboard presentation.


## Phase 3 schema adaptability

This version adds a canonical telemetry mapping layer.

The collector can now ingest:

- Native AegisTelemetry events
- Generic live-service multiplayer telemetry
- Unreal-style dedicated server/network telemetry

Source profiles live in:

```text
source_schemas/
```

New endpoints:

```text
GET  /v1/source-profiles
POST /v1/events
POST /v1/events/{source_profile}
```

Demo alternate schema ingestion:

```bash
cd simulator
python generate_generic_traffic.py --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120
python generate_unreal_traffic.py --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120
```

The dashboard includes a `Source Schemas` workspace to inspect supported adapters and observed source profiles.


## Phase 3.1 source profile filtering

This version makes `source_profile` a first-class analytics dimension across aggregates, incidents, quality failures, and dashboard filters.

When running multiple generators at once, you can now filter the dashboard by:

- All source profiles
- `aegis_default`
- `generic_live_service`
- `unreal_multiplayer`

Because ClickHouse table schemas changed, reset local volumes:

```bash
docker compose down -v
docker compose up --build
```


## ClickHouse migration patch

If upgrading from an older local volume, the dashboard may report:

```text
Unknown expression identifier 'source_profile'
```

This version includes a `clickhouse-migrate` service that adds the missing `source_profile` columns to existing ClickHouse tables.

Run:

```bash
docker compose down
docker compose up --build
```

A full reset is optional:

```bash
docker compose down -v
docker compose up --build
```


## FastAPI 422 collector fix

If the simulator returns:

```text
422 Client Error: Unprocessable Entity
```

rebuild this patched version:

```bash
docker compose down
docker compose up --build
```

The collector now explicitly accepts arbitrary JSON request bodies for `/v1/events` and `/v1/events/{source_profile}`.


## ClickHouse migration retry fix

If `clickhouse-migrate` exits with code `210`, run:

```bash
docker compose down --remove-orphans
docker compose up --build
```

This version retries ClickHouse migrations until the native client port is ready. For a completely clean demo database, run:

```bash
docker compose down -v
docker compose up --build
```


## Local reset instead of migration service

This version removes the `clickhouse-migrate` service. When upgrading schemas locally, reset the ClickHouse volume:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

This recreates the ClickHouse tables from `infra/clickhouse/init.sql` using the current schema.


## Phase 3.2 dashboard visual redesign

This version redesigns the Streamlit dashboard to use a sharper, more professional visual system inspired by the attached Guerrilla-style careers layout.

Key updates:

- Removed rounded corners from tabs, cards, alerts, metrics, and data surfaces
- Switched to a sharp dark-slate + light-panel palette with stronger contrast
- Added premium Altair time-series charts with a colorblind-safe series palette
- Improved table legibility and navigation with clearer borders and heights
- Updated the hero/header and workspace navigation to a more editorial, studio-like layout


## Phase 3.3 dashboard refinement

This version refines the sharp dashboard design with:

- tighter typography
- stronger sidebar hierarchy
- operational status banner
- severity-coded incident cards
- clearer incident evidence drilldown
- improved chart/table consistency
- square-edged executive dashboard layout


## Phase 3.4 modular dashboard architecture

The dashboard has been refactored from one large `app.py` into smaller modules:

- `config.py`
- `query.py`
- `sidebar.py`
- `styles.py`
- `components.py`
- `charts.py`
- `schemas.py`
- `workspaces.py`
- `views/*.py`

To add or remove dashboard workspaces, edit `services/dashboard/workspaces.py`.
To add new charts, prefer `services/dashboard/charts.py`.
To add new source schemas, add JSON profiles under `source_schemas/`.


## Dashboard import fix

If Streamlit reports `ModuleNotFoundError: No module named 'services'`, rebuild this version:

```bash
docker compose down --remove-orphans
docker compose up --build
```

The dashboard Docker image now sets `PYTHONPATH=/app` and copies `services/__init__.py`.


## Phase 4 recommendation intelligence

This version upgrades incidents from generic recommendations to a richer recommendation engine with ranked issue candidates, owners, evidence, specific actions, investigation steps, validation plans, guardrail metrics, and tradeoffs. Reset ClickHouse because the aggregate schema changed:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```


## Phase 4.1 custom recommendation rules

The recommendation engine is now data-driven.

Developers can add/edit issue conditions and solution guidance in JSON files under:

```text
recommendation_rules/
```

The active profile is selected with:

```text
RECOMMENDATION_RULE_PROFILE=default_recommendation_rules
```

The dashboard includes a `Recommendation Rules` workspace explaining available rule profiles and how to add new rules.


## Default out-of-the-box recommendation rules

The default recommendation profile now includes the complete built-in issue set:

- AoE replication overload
- Physics simulation spike
- Network packet pressure
- Local density tick-budget pressure
- AI pathfinding pressure
- Memory pressure / allocation churn
- Regional capacity / matchmaking surge
- Desync / hit-registration risk


## Phase 5 rule testing and replay

Recommendation rules now have a test/replay layer.

New sample metrics live under:

```text
recommendation_rules/tests/
```

Run rule tests:

```bash
python tools/test_recommendation_rules.py --profile default_recommendation_rules
```

Preview one sample:

```bash
python tools/preview_recommendation.py recommendation_rules/tests/ai_pathfinding_pressure_sample.json
```

The dashboard includes a `Rule Testing` workspace that lets developers preview expected vs actual issue candidates for rule profiles and sample telemetry windows.


## Phase 5.1 incident severity filter

The Incident Dossier now includes a severity filter:

- All severities
- Critical only
- Warnings only

It also shows severity distribution for the selected source/region/server/time-window scope.


## Phase 5.2 incident rule ID filter

The Incident Dossier can now filter by both:

- incident severity
- rule ID / likely driver

Rule ID options are loaded from configured recommendation rule profiles and observed incidents, so built-in and custom rules are available to analysts.


## Phase 6 incident timeline

The dashboard now includes an `Incident Timeline` workspace.

This view lets analysts select an incident and replay the telemetry before/during/after the trigger window for the same source profile, server, map, and zone.

It shows:

- root-cause sequence table
- density/frame/risk timelines
- AoE/physics/network pressure timelines
- player-impact timelines
- memory/CPU/AI timelines
- top event type and top ability ID context
- recommendation changes over time


## Phase 6.1 configurable timeline stages

Incident Timeline root-cause stages are now configurable through JSON profiles under:

```text
timeline_stages/
```

The default profile includes rule-specific stage sequences for all out-of-the-box recommendation rules:

- AoE replication overload
- Physics simulation spike
- Network packet pressure
- Local density tick-budget pressure
- AI pathfinding pressure
- Memory pressure / allocation churn
- Regional capacity / matchmaking surge
- Desync / hit-registration risk
- Unclassified performance pressure

The dashboard also includes a `Timeline Stages` workspace for developers.


## Phase 6.2 incident timeline selection fix

The Incident Timeline now:

- defaults to `default_timeline_stages` instead of the alphabetically first profile
- keeps the selected incident pinned across live refreshes using stable `incident_id` session state
- adds an optional `Auto-follow latest incident` checkbox for analysts who want the newest incident selected automatically

This fixes the issue where every incident appeared to show the same three custom example stages.


## Phase 6.3 timeline wrapping and grouped navigation

The Incident Timeline root-cause sequence now renders as wrapped cards, with the original table kept in an expander. Low-contrast blue text is forced to white for readability.

Dashboard workspaces are now grouped into dropdown sections:

- Operations
- Incidents
- Rules & Replay
- Data & Schemas

The navigation uses native Streamlit widgets and CSS transitions for smooth, performant behavior during live refresh.


## Phase 6.4 two-tier tab navigation

Workspace navigation now uses a two-level tab bar instead of dropdowns.

Top row:

- Operations
- Incidents
- Rules & Replay
- Data & Schemas

Lower row shows the workspaces inside the selected group.

The extra “Workspace Navigation / Grouped Operations Dossiers” description block has been removed.


## Phase 6.5 distinct sub-navigation

The two-tier workspace navigation now clearly distinguishes the lower row as sub-navigation using a smaller scale, inset strip, accent bar, and lighter active state.


## Phase 6.6 hover-expanded workspace subnavigation

Workspace navigation now uses a hover-expanded two-level menu. Top-level groups are always visible, and hovering over a group reveals its sub-workspaces. Moving outside collapses the sub-navigation automatically.

The workspace content region now shows a breadcrumb title such as `Operations [separator image] Command Center`.


## Phase 6.7 incident timeline session state warning fix

Fixed the Streamlit warning caused by manually assigning the same session-state key used by the Incident Timeline stage-profile selectbox.


## Phase 6.8 hover navigation polish

Hover subnavigation now uses dark text on the light dropdown background, selected subnav items are indicated only with a blue underline, the breadcrumb uses a custom white SVG arrow, and subnav links target the same browser tab.


## Phase 6.9 state-driven workspace navigation

Workspace navigation now uses Streamlit widget state instead of HTML links/query parameters. Switching tabs no longer opens a new browser tab or performs browser-level page navigation; the dashboard stays on the same page and updates the selected workspace area.


## Phase 6.10 state-driven hover-style navigation

Navigation now combines hover/dropdown styling with state-driven workspace switching. It uses no HTML links or query parameters, so switching workspaces no longer opens a new tab or performs browser-level navigation. The subnavigation is collapsed by default and expands on hover.


## Phase 6.11 robust state-driven hover navigation

Navigation now uses a keyed Streamlit container plus marker-based CSS selectors so the subnavigation is hidden by default and appears only while hovering the top navigation region. Workspace switching remains state-driven with no links, hrefs, query parameters, or browser-level navigation.


## Phase 6.12 final state-driven hover navigation fix

Navigation CSS now targets the Streamlit radio groups by accessibility label instead of fragile wrapper/sibling selectors. The subnavigation is hidden by default and appears only on hover, while workspace switching remains state-driven with one-click updates through radio callbacks.


## Phase 6.13 per-group state-driven hover navigation

Navigation now renders one hidden subnavigation radio per main group, so hovering over any group shows that group’s own subnav. The subnav remains open while moving from the top tab into the dropdown, and workspace switching remains state-driven with no links, hrefs, query parameters, or browser-level navigation.


## Phase 6.14 subnavigation gap and width fix

The hover subnavigation now sits directly beneath the primary group tab, includes a small hover bridge so it does not disappear while moving the cursor downward, and shrink-wraps to the last subnav tab instead of stretching across the page.


## Phase 6.15 navigation positioning and clickability fix

The hover subnav is now positioned directly beneath the primary nav with no visual gap. A small invisible hover bridge keeps it open while moving the cursor down, and the dropdown shrink-wraps to its tabs instead of extending across the page.


## Phase 6.16 flow-based subnav fix

The hover subnav no longer uses pixel-based absolute positioning. It now expands in normal document flow directly under the hovered main tab, removing the gap and making subnav tabs clickable while keeping state-driven navigation.


## Phase 6.17 selected main-tab hover text fix

Fixed the selected main navigation tab hover state so the text turns dark gray/black when the selected tab background becomes light. This prevents white-on-white text while preserving the blue underline.


## Phase 6.18 left navigation dropdown font fix

Sidebar/left-navigation dropdown text now matches the workspace tab styling: dark gray text, uppercase lettering, stronger font weight, compact tracking, square borders, and a light tab-like dropdown background.


## Phase 6.19 remove top white dashboard strip

Removed the default Streamlit top header/toolbar strip and aligned the app shell background with the dashboard background so the hero starts cleanly without a white band above it.


## Phase 6.20 global dropdown style

Dropdown/selectbox typography and field styling now match the left-navigation dropdown across all workspaces. All dropdown values and opened menu options use dark gray uppercase text, stronger weight, compact tracking, square borders, and a light tab-like background.


## Phase 6.21 incident timeline HTML render fix

Fixed raw HTML appearing in the Incident Timeline root-cause sequence by rendering each timeline card with its own safe `st.markdown(..., unsafe_allow_html=True)` call instead of joining all cards into one large HTML block.


## Phase 6.22 subnavigation button fix

Subnavigation items now use Streamlit buttons instead of per-group radios. This fixes the inactive-group edge case where clicking a group's already-selected/default subnav item did not fire a state change. Navigation remains state-driven with no links, hrefs, query parameters, or browser-level navigation.


## Phase 6.23 horizontal button subnav fix

Button-based subnavigation now renders horizontally again using Streamlit columns plus CSS that keeps the subnav as a single horizontal tab strip. This preserves the one-click state-driven button behavior from Phase 6.22 while restoring the original horizontal dropdown layout.


## Phase 6.24 Streamlit column gap fix

Fixed the dashboard crash caused by `st.columns(..., gap=None)`. Streamlit only accepts `"small"`, `"medium"`, or `"large"`, so the subnav now uses `gap="small"` while CSS keeps the horizontal tab strip visually tight.


## Phase 6.25 navigation label width fix

Navigation labels now use content-weighted column sizing so longer labels like `Recommendation Rules` are not clipped. Additional CSS prevents Streamlit/BaseWeb button internals from truncating tab text.
