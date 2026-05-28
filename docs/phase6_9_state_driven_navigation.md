# Phase 6.9 — State-Driven Workspace Navigation

This patch removes browser-level navigation from workspace switching.

## Problem

The previous hover subnavigation used HTML links and query parameters. That made workspace switching behave like browser navigation and could feel like a full page refresh or open a new tab.

## Fix

Workspace switching now uses native Streamlit radio widgets and session state:

```text
aegis_active_workspace_key
```

The URL remains stable, no new tab opens, and the selected workspace region updates inside the dashboard.

## Performance

Streamlit still reruns the script internally when a widget changes, but cached query functions remain in place. This avoids browser navigation and gives the expected same-page workspace-switching behavior.
