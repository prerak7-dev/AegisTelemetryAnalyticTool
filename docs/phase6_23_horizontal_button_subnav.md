# Phase 6.23 — Horizontal Button Subnav Fix

This patch fixes the issue where the button-based subnavigation rendered vertically.

## Root cause

Phase 6.22 replaced subnav radios with buttons to fix the inactive-group click issue. However, the buttons were rendered inside a normal Streamlit vertical container, so they stacked vertically.

## Fix

The subnav buttons now render inside `st.columns(...)`:

```python
subnav_columns = st.columns(len(group.workspace_keys), gap=None)
```

Additional CSS forces the subnav horizontal block/columns to behave like a single horizontal tab strip.

## Guarantees

- subnav remains state-driven
- buttons still fire even for already-selected/default inactive-group items
- no links
- no hrefs
- no query parameters
- horizontal Phase 6.8-style tab strip restored
