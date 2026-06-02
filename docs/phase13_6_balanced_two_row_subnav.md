# Phase 13.6 — Balanced Two-Row Subnav Layout

This patch fixes the remaining visual inconsistencies in the two-row workspace subnav.

## Fixed

```text
Rows with fewer tabs no longer leave empty trailing panel space.
Rows with longer labels no longer protrude past the panel edge.
Both rows fill the same dropdown width.
Tabs distribute evenly inside their row.
Borders align cleanly across rows.
```

## Root cause

The previous implementation split long subnav groups into two rows, but each row still used label-length-based Streamlit column weights. That caused:

```text
upper row: small leftover gap
lower row: tab width mismatch / protruding edge
```

## Fix

For long/two-row subnav groups, navigation now uses equal column weights for each row:

```python
[1 for _ in row_keys]
```

This makes each row independently distribute its tabs across the full dropdown width.

The CSS also forces the row, columns, containers, and buttons to use the same full-width box model.
