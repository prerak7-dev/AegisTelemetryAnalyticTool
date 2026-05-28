# Phase 7.2.5 — Canonical Filter State Fix

This patch fixes live-refresh filter resets by separating widget state from canonical filter state.

## Root cause

The previous implementation used stable widget keys and URL query parameters, but the widgets themselves could still be rebuilt at default values during refresh cycles.

## Fix

The sidebar now stores selections in a dedicated canonical state object:

```text
st.session_state["aegis_persisted_filters"]
```

Each widget has an `on_change` callback that mirrors its value into the canonical object immediately.

Before every widget is rendered, the widget key is restored from the canonical object. If canonical state is unavailable, the value is restored from URL query parameters. If that is unavailable, the default is used.

## Persistence order

```text
1. Canonical filter state: aegis_persisted_filters
2. URL query parameters
3. Default values
```

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
