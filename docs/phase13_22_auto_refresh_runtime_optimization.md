# Phase 13.22 — Auto Refresh Runtime Optimization

This phase adds a workspace-aware refresh coordinator.

## Added

```text
workspace refresh policies
live/static/manual/demo workspace modes
effective refresh interval calculation
jitter support
auto-refresh skipping for static/manual workspaces
KPI strip skipping for static/manual workspaces
manual refresh telemetry
auto-refresh telemetry
Query Performance refresh runtime panel
documentation page for refresh runtime
```

## New files

```text
services/dashboard/refresh_runtime.py
docs/toolkit/operations_reference/auto_refresh_runtime.md
docs/phase13_22_auto_refresh_runtime_optimization.md
```

## Updated files

```text
services/dashboard/app.py
services/dashboard/sidebar.py
services/dashboard/views/query_performance.py
services/dashboard/performance_config.py
config/dashboard_performance.json
config/documentation_navigation.json
README.md
```

## Key behavior

Static and manual workspaces no longer install an auto-refresh timer even when global Live Refresh is enabled.

Examples:

```text
Documentation: static
Performance Config: static
Analyst Toolkit: manual
Query Performance: manual
Command Center: live
Demo Control Center: demo
```

This reduces unnecessary reruns and ClickHouse queries while preserving responsive live dashboards.
