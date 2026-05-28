# Phase 7.2.4 — Durable Filter Persistence

This patch strengthens sidebar filter persistence during live refresh.

## Problem

The Phase 7.2.1 sidebar used stable `st.session_state` keys, but some refresh cycles could still rebuild widgets with default values.

## Fix

Sidebar filters now persist in two layers:

```text
1. st.session_state
2. URL query parameters
```

If widget state is missing or invalid during an autorefresh rerun, the sidebar restores the value from query parameters before rendering the selectbox.

## Persisted controls

```text
Live refresh
Refresh interval
Analysis window
Source profile
Region
Server
Table row limit
```

## Behavior

Selections only reset if the previous value is no longer available in the current option list.
