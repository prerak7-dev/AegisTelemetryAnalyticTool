# Phase 13.23.5 — Auto Refresh Session Safety Fix

This patch addresses intermittent Streamlit websocket/session initialization errors.

## Symptom

```text
Bad message format
Tried to use SessionInfo before it was initialized
```

## Root cause

The auto-refresh component was mounted inside the sidebar. On some runs, especially during first page load, rapid rebuilds, or workspace changes, the component can try to communicate before Streamlit has fully initialized the session.

## Fix

The auto-refresh component is no longer rendered inside the sidebar.

Instead, auto-refresh is mounted at the very end of the page render:

```text
set page config
inject styles
render hero
render navigation
render sidebar
render filters
render KPI strip
render workspace
mount auto-refresh controller last
```

The component now also uses a stable key:

```text
aegis_safe_live_refresh_tick
```

instead of a workspace-specific dynamic key. This avoids recreating the component when switching workspaces.

## Updated files

```text
services/dashboard/app.py
services/dashboard/sidebar.py
```
