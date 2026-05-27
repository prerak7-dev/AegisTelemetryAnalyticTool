# Dashboard Modular Architecture

Phase 3.4 refactors the dashboard into small, editable modules.

## File layout

```text
services/dashboard/
  app.py                  # thin Streamlit entrypoint
  config.py               # constants, env vars, filter dataclass
  query.py                # ClickHouse client, cached queries, SQL filter helpers
  sidebar.py              # source/region/server/time filters
  styles.py               # all CSS in one place
  components.py           # KPI cards, tables, hero, incident cards
  charts.py               # reusable Altair chart helpers
  schemas.py              # source schema profile loading
  workspaces.py           # workspace registry
  views/
    command_center.py
    selected_server.py
    incident_dossier.py
    data_quality.py
    scaling_readiness.py
    source_schemas.py
```

## How to add a new workspace

1. Create a file:

```text
services/dashboard/views/my_new_view.py
```

2. Add:

```python
def render(context):
    ...
```

3. Register it in `services/dashboard/workspaces.py`:

```python
from services.dashboard.views import my_new_view

WORKSPACES = [
    ...
    Workspace("my_new_view", "My New View", my_new_view.render),
]
```

## How to remove a workspace

Remove its entry from `WORKSPACES` in:

```text
services/dashboard/workspaces.py
```

## How to add a chart

Prefer using `services/dashboard/charts.py`.

Existing helper:

```python
render_timeseries_chart(df, x="window_start", y="p95_frame", series="region")
```

If a new chart type is needed, add a reusable helper to `charts.py` rather than embedding chart configuration directly inside a workspace.

## How to add a table

Use:

```python
from services.dashboard.components import render_table

render_table(df, height=360)
```

## How to add a source schema

Add a new JSON profile under:

```text
source_schemas/
```

Then rebuild. The Source Schemas workspace loads it automatically.
