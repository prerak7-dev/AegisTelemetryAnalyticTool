# Auto Refresh Runtime

Phase 13.22 adds a workspace-aware auto-refresh runtime.

## Why this exists

A Streamlit auto-refresh can rerun the full app. That is acceptable for a small demo, but it becomes wasteful when static pages, documentation, configuration views, and analyst tools refresh as often as live dashboards.

The refresh runtime separates:

```text
live operational workspaces
incident workspaces
demo workspaces
manual analytical workspaces
static documentation/configuration workspaces
```

## Policy file

Refresh behavior is configured in:

```text
config/dashboard_performance.json
```

under:

```text
refresh_runtime
```

## Workspace modes

| Mode | Behavior |
|---|---|
| live | Auto-refresh enabled when global live refresh is on |
| incident | Auto-refresh enabled but usually slower than live |
| demo | Auto-refresh enabled and can be faster during scenario warmup |
| manual | Does not auto-refresh; use Refresh Now |
| static | Does not auto-refresh and skips fleet KPI strip |

## Example policy

```json
{
  "documentation": {
    "mode": "static",
    "auto_refresh": false,
    "render_kpi_strip": false
  },
  "command_center": {
    "mode": "live",
    "auto_refresh": true,
    "interval_multiplier": 1.0,
    "render_kpi_strip": true
  }
}
```

## Runtime behavior

The runtime checks:

```text
active workspace
global live refresh toggle
workspace refresh mode
configured interval multiplier
min/max interval limits
jitter setting
```

It then decides whether to install the auto-refresh timer.

## KPI strip optimization

Static/manual workspaces can skip the fleet KPI strip:

```text
Documentation
Performance Config
Analyst Toolkit
Rule definitions
```

This avoids extra ClickHouse work on pages that do not need live fleet status.

## Refresh telemetry

Refresh events are visible in:

```text
Data & Schemas > Query Performance
```

The workspace shows:

```text
workspace refresh mode
auto-refresh on/off
recent refresh count
skipped refresh count
recent refresh history
```

## Adding a new workspace

When adding a workspace in:

```text
services/dashboard/workspaces.py
```

also add a refresh policy in:

```text
config/dashboard_performance.json
```

Recommended defaults:

```text
live operational dashboard:
  mode = live

incident evidence page:
  mode = incident

analyst workflow:
  mode = manual

documentation/config page:
  mode = static

demo launcher:
  mode = demo
```

If no policy is configured, the default workspace policy is used.
