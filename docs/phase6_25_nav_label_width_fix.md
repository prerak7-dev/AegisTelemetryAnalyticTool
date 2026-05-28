# Phase 6.25 — Navigation Label Width Fix

This patch fixes clipped navigation labels such as:

```text
Recommendation Rules
```

## Root cause

The button-based subnavigation used equal-width Streamlit columns. Long labels were forced into the same width as short labels and could be clipped.

## Fix

The main navigation and subnavigation now use content-weighted column ratios:

```python
group_column_weights = [
    max(14, len(group.label) + 6)
    for group in WORKSPACE_GROUPS
]

subnav_column_weights = [
    max(14, len(workspace_by_key(workspace_key).label) + 6)
    for workspace_key in group.workspace_keys
]
```

Additional CSS prevents BaseWeb/Streamlit button internals from clipping text.

## Behavior preserved

- subnav remains horizontal
- button-based one-click inactive-group fix remains
- no links
- no hrefs
- no query parameters
- no browser-level navigation
