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


## Phase 7 multi-dimensional live pressure command center

Command Center now promotes all major live degradation signals into first-class pressure cards and trends instead of making p95 server frame time the only headline metric.

New pressure dimensions:

- Simulation
- Network
- Replication
- Physics
- Memory
- AI
- Matchmaking
- Player Impact
- Telemetry Quality

The Command Center includes pressure cards, normalized pressure timelines, pressure ranking, pressure drilldown, frame-time symptom view, and source/regional pressure summary.


## Phase 7.1 query performance foundation and baseline intelligence preparation

This phase improves the dashboard query workflow before expanding into later analytics phases.

Added:

- named query diagnostics
- query cache TTL tiers: `live`, `short`, `medium`, `static`
- `Data & Schemas > Query Performance` workspace
- lazy Command Center drilldown sections
- baseline anomaly preview comparing current windows against recent historical source/region/server/map/zone behavior

This prepares the tool for dynamic thresholds, build regression analysis, fix validation, incident workflow, demo scenarios, analyst notebooks, and production readiness work.


## Phase 7.2 query architecture hardening

Phase 7.2 adds a configurable performance layer for the dashboard.

Added:

- `config/dashboard_performance.json`
- `services/dashboard/performance_config.py`
- configurable table names
- configurable pressure scoring budgets
- configurable query budgets
- configurable cache TTLs
- configurable dashboard limits
- configurable baseline windows and anomaly weights
- query over-budget diagnostics
- `Data & Schemas > Performance Config` workspace
- optional ClickHouse rollup SQL templates in `sql/phase7_2_query_architecture_hardening.sql`

This keeps the tool adaptable for different games, server models, regions, platforms, and studio telemetry conventions without requiring code edits for every threshold or table-name change.


## Phase 7.2.1 navigation and filter persistence fix

Fixed the `Data & Schemas > Performance Config` subnavigation rendering outside the browser window by moving subnavigation into a full-width responsive row. Sidebar filters now persist across live refresh through stable `st.session_state` keys. A visible filtered-data scope strip now appears above the workspace content, and tables are wrapped in a horizontal-scroll shell for wide evidence views.


## Phase 7.2.2 sidebar selectbox format function fix

Fixed a Streamlit sidebar crash caused by passing `format_func=None` into persisted selectboxes. The sidebar helper now only passes `format_func` when a callable is provided, preserving filter persistence across auto-refresh without causing `'NoneType' object is not callable`.


## Phase 7.2.3 subnavigation alignment fix

Restored the working per-group hover subnavigation model so subnav tabs appear directly below the hovered main tab and remain clickable. Right-edge groups now align their subnav to the right, keeping long rows such as `Data & Schemas > Performance Config` inside the viewport without detaching the row from the main navigation.


## Phase 7.2.4 durable filter persistence

Strengthened sidebar filter persistence during live refresh. Filters now persist in both `st.session_state` and URL query parameters, so auto-refresh reruns restore the selected source profile, region, server, analysis window, refresh interval, table row limit, and live-refresh state before widgets render.


## Phase 7.2.5 canonical filter state fix

Fixed live-refresh filter resets by separating widget state from canonical persisted filter state. Sidebar widgets now mirror every selection into `st.session_state["aegis_persisted_filters"]` through callbacks and restore widget keys from that canonical object before rendering.


## Phase 7.3 baselines, anomaly detection, and dynamic thresholds

Added `Incidents > Baseline Intelligence`, a context-aware anomaly workspace that compares the active filtered window against recent historical behavior for the same source/region/server/map/zone or broader configurable scopes.

The phase adds dynamic thresholds, ratio-to-baseline, z-score, anomaly severity, dominant anomaly metric, baseline confidence, and optional SQL templates for a future `baseline_anomaly_windows` rollup table.


## Phase 8 build regression analysis

Added `Incidents > Build Regression`, a build-to-build comparison workspace for release readiness and performance regression triage. The workspace compares a previous build against a current build using configurable metrics, weights, directions, confidence requirements, and severity thresholds.

The simulator now supports `--build-version` and `--build-regression-mode` so demo data can be generated for baseline, regressed, or improved candidate builds.


## Phase 9 experimentation and fix validation

Added `Rules & Replay > Fix Validation`, a control/treatment analysis workspace for validating whether recommended optimizations improved primary performance metrics without regressing guardrails. The simulator now supports `--experiment-id`, `--experiment-variant`, and `--fix-validation-mode`.


## Phase 10 alerting, ownership, and incident workflow

Added `Incidents > Incident Workflow`, a local workflow layer for assigning incident owners, tracking status, adding analyst notes, monitoring SLA state, writing resolution summaries, and generating exportable incident reports. Workflow settings are configurable in `config/dashboard_performance.json`, and optional ClickHouse production tables are included in `sql/phase10_incident_workflow.sql`.


## Phase 11 portfolio demo mode and scenario library

Added `Demo > Demo Control Center`, a portfolio-ready scenario launcher and runbook workspace. Scenarios are configured in `config/demo_scenarios.json`, and launch/reset behavior is controlled through `config/dashboard_performance.json` under `demo_control_center`.


## Phase 11.1 demo configuration packaging fix

Fixed Demo Control Center runtime packaging so `config/demo_scenarios.json` and `simulator/generate_traffic.py` are available inside the dashboard container. The dashboard service now mounts `./config`, `./simulator`, and `./data`, enabling editable scenario configs, dashboard-launched traffic generation, resettable demo data, local scenario history, and host/container command generation.


## Phase 11.2 demo UX and fast feedback loop

Improved Demo Control Center number-input styling and added a Live Demo Feedback panel. The panel shows generator state, raw event ingestion, aggregate window availability, incidents, max risk, and latest data ages so the demo no longer feels silent while the processor waits for aggregate windows to close.


## Phase 11.3 demo action controls styling

Updated Demo Control Center action buttons and the sidebar refresh button to match the sharp tab visual language. Reset confirmation is now grouped with the reset button and labeled clearly as `Confirm reset of demo telemetry tables`.


## Phase 12 data export, analyst notebooks, and SQL templates

Added `Data & Schemas > Analyst Toolkit`, a workspace for filter-aware SQL template execution, CSV/JSON exports, downloadable SQL templates, and downloadable analyst notebooks. This phase adds notebooks for hot-zone analysis, build regression, fix validation, and rule quality review, plus SQL templates for common investigation workflows.


## Phase 12.5 professional documentation workspace

Added `Data & Schemas > Documentation`, a configuration-backed professional documentation workspace with its own hierarchical navigation, search, page outline, user guide, developer guide, data reference, operations reference, and markdown page downloads. Documentation navigation lives in `config/documentation_navigation.json`, and markdown pages live under `docs/toolkit/`.


## Phase 13 production readiness layer

Added production-readiness assets: OpenAPI contract, contract tests, collector `/metrics` endpoint, Prometheus scrape config, Grafana dashboard seed, OpenTelemetry collector starter config, Kafka retention/DLQ documentation, ClickHouse partitioning/TTL documentation, collector load-test profile, deployment checklist, readiness checklist, and production-readiness pages in the documentation workspace.


## Phase 13.1 subnav viewport alignment fix

Fixed long workspace subnav rows clipping outside the browser viewport. Navigation now right-aligns long or right-edge subnav groups based on the workspace registry, so Data & Schemas remains fully visible after adding Analyst Toolkit and Documentation.


## Phase 13.2 robust subnav layout fix

Reworked workspace navigation so subnav rows render in a full-width overlay layer instead of inside individual group columns. This fixes Data & Schemas clipping after adding Performance Config, Analyst Toolkit, and Documentation, while preserving hover behavior and state-driven Streamlit button navigation.


## Phase 13.3 hover-stable viewport-fit subnav

Replaced the failed full-layer `:has()` hover approach with a reliable per-group hover subnav. Long or right-side subnavs now shift to the nav content edge and can wrap to two rows if needed, while small subnavs remain aligned to their main tab.


## Phase 13.4 right-aligned long subnav

Fixed long subnav groups such as Data & Schemas by shifting the dropdown left to align with the right edge of the dashboard content viewport and by structurally splitting long subnavs into two rows, so all tabs remain visible without zooming out.


## Phase 13.5 two-row subnav visual polish

Polished the long two-row workspace subnav so it no longer clips content or shows internal scrollbars. The subnav now uses consistent row height, button spacing, readable labels, and restores the blue underline for hover and active states.


## Phase 13.6 balanced two-row subnav layout

Balanced long two-row workspace subnavs by using equal-width columns per row and full-width row styling. This removes empty trailing space, prevents tabs from protruding past the panel, and keeps row borders aligned.


## Phase 13.7 consistent subnav row strategy

Updated subnav row splitting so odd five-tab groups remain as one row instead of an uneven 3/2 layout. Even long groups such as Data & Schemas keep the clean 3/3 two-row layout. This removes empty trailing panel space and avoids tabs protruding past the panel edge.


## Phase 13.8 customizable adaptive subnav layout

Replaced manual subnav row splitting with an adaptive flex-based layout. Subnav buttons are rendered sequentially and CSS handles wrapping, last-row stretching, hover/active underline states, and viewport-safe alignment. This makes the navigation robust when developers add or remove workspaces without requiring design recalibration.


## Phase 13.9 horizontal adaptive subnav grid

Updated the customizable subnav to use a horizontal CSS-grid layout instead of a vertical flex stack. Subnav tabs remain horizontal, wrap into additional horizontal rows only when needed, stay inside the dashboard content viewport, and keep hover/active blue underline states without manual row splitting.


## Phase 13.10 robust horizontal workspace subnav

Replaced the experimental subnav CSS with an isolated `aegis_v2_*` navigation implementation. Subnavs are rendered as horizontal Streamlit column rows, compact groups align with their main tab, long/overflow-risk groups use the full dashboard content nav-row width, and large custom groups create balanced horizontal rows automatically.


## Phase 13.11 dynamic compact subnav width

Refined the v2 navigation so small subnav groups, such as Demo with one option, stay compact instead of expanding to the full dashboard nav-row width. Compact groups now use dynamic width based on option labels and right-align near the viewport edge when needed.


## Phase 13.12 hierarchical documentation side navigation

Replaced the Documentation workspace's section dropdown and page radio selector with a professional hierarchical expanding side navigation. Sections expand vertically and pages render as state-driven buttons with active/hover styling matched to the Aegis dashboard theme.


## Phase 13.13 form control containment polish

Added CSS containment for documentation badges, Demo Control Center number inputs, number steppers, reset confirmation controls, and action buttons. This prevents inner controls from spilling outside bordered cards while preserving the current visual design.


## Phase 13.14 documentation badge inner padding

Refined the Documentation workspace audience badge so it no longer touches the right edge of the side-nav panel. The badge now has symmetric left/right inset spacing while staying fully contained.


## Phase 13.15 consistent control inset system

Generalized the documentation badge padding fix across similar bordered controls. Documentation side-nav controls, Demo Control Center number inputs, reset checkbox/button/caption, action buttons, and sidebar refresh now use consistent symmetric insets and defensive box sizing.


## Phase 13.16 global design-system hardening

Added an app-wide square-edge and containment layer for Streamlit/BaseWeb controls. Documentation navigation, audience badges, Demo Control Center number inputs, reset controls, action buttons, and future Aegis keyed controls now share consistent padding, margins, border-box sizing, no rounded corners, and no visual spill outside bordered panels.


## Phase 13.17 number input stepper containment fix

Fixed Demo Control Center number inputs so the text field and minus/plus steppers stay inside the bordered card. The number input now uses a contained flex model with fixed-width stepper buttons, square edges, and no right-edge clipping.


## Phase 13.18 demo numeric text inputs

Replaced the Demo Control Center duration/EPS number inputs with contained numeric text inputs to eliminate clipped BaseWeb `- / +` stepper controls. Values are parsed and clamped in Python, keeping the same scenario command behavior while restoring consistent square-edged layout.


## Phase 13.19 control stepper and card spacing polish

Added custom contained numeric steppers for Demo Control Center duration and events-per-second controls, restoring visible `- / +` controls without relying on clipped native number-input steppers. Also improved Command Center metric/pressure card spacing so cards read as individual panels rather than split-column background slabs.


## Phase 13.20 custom stepper state and layout fix

Fixed the Demo Control Center custom numeric stepper. The text input widget now uses a separate widget key from the canonical parsed value key, preventing StreamlitAPIException. The stepper row now uses fixed-width minus/plus columns so both controls remain fully visible inside the card.


## Phase 13.21 custom stepper visibility fix

Fixed the Demo Control Center custom stepper so the input value and the `+` sign are visible. The row now allows label + input height, widens the stepper columns, and only applies fixed height to the actual input/button controls.


## Phase 13.22 auto refresh runtime optimization

Added a workspace-aware refresh coordinator with configurable live/static/manual/demo policies. Static and manual workspaces no longer install the auto-refresh timer, static/manual workspaces can skip the fleet KPI strip, effective refresh intervals support policy multipliers and jitter, and Query Performance now includes auto-refresh runtime telemetry.


## Phase 13.23 live snapshot tables and lightweight queries

Added ClickHouse live snapshot views and dashboard fallback logic. KPI strip, sidebar filters, and Command Center live queries now prefer lightweight snapshot views when available, while safely falling back to aggregate tables for existing developer volumes. Includes `sql/live_snapshot_tables.sql` and `tools/apply_live_snapshot_tables.py` for applying snapshot views to existing ClickHouse instances.


## Phase 13.23.1 ClickHouse snapshot init fix

Fixed ClickHouse startup failures from the Phase 13.23 snapshot SQL. Snapshot views now use `DROP VIEW IF EXISTS` + `CREATE VIEW` instead of `CREATE OR REPLACE VIEW`, and staleness calculations avoid aggregate expressions directly inside `dateDiff`. If ClickHouse already failed during first initialization, reset the local dev volume with `docker compose down -v --remove-orphans` before rebuilding.


## Phase 13.23.2 ClickHouse snapshot aggregation safety fix

Fixed ClickHouse `ILLEGAL_AGGREGATION` errors from live snapshot views. The default local snapshot views are now pass-through views over `agg_zone_30s`, so the dashboard can safely aggregate over them. Optional snapshot views are no longer created during ClickHouse init; apply them manually with `python tools/apply_live_snapshot_tables.py` after ClickHouse is healthy. If ClickHouse failed during init, run `docker compose down -v --remove-orphans` before rebuilding.


## Phase 13.23.3 Command Center snapshot scope fix

Fixed a Command Center runtime `NameError` where `render_pipeline_health()` referenced `live_pressure_table` outside its local scope. The pipeline health helper now resolves its own preferred live table and uses a ClickHouse-safe staleness subquery.


## Phase 13.23.4 alert text theme and runtime notice cleanup

Updated all Streamlit alert/info/warning/error containers so text and icons use grayish-white dashboard colors. Removed the sidebar refresh-policy caption and the Command Center Phase 13.23 snapshot notice callout to keep runtime optimization details out of the main operator UI.


## Phase 13.23.5 auto refresh session safety fix

Moved the Streamlit auto-refresh component out of the sidebar and into an end-of-render controller in `app.py`. The component now mounts after the page, sidebar, filters, KPI strip, and workspace render, reducing intermittent `Bad message format / SessionInfo before initialized` errors. The auto-refresh component also uses a stable key instead of a workspace-specific dynamic key.
