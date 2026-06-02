# Phase 13.2 — Robust Subnav Layout Fix

This patch replaces the previous width-estimation fix with a structural navigation fix.

## Root cause

The Data & Schemas subnav had grown to six tabs:

```text
Data Quality
Source Schemas
Query Performance
Performance Config
Analyst Toolkit
Documentation
```

The previous layout rendered the subnav inside the hovered main-group column. Even when the CSS attempted to right-align the row, Streamlit's column structure still constrained the available viewport area, causing later tabs to be clipped.

## Fix

The navigation now renders:

```text
main group row
  +
full-width subnav overlay layer
```

Subnav rows are no longer children of the individual group columns.

## Behavior

```text
Hover main group
  ↓
CSS reveals that group's full-width subnav row
  ↓
Buttons remain state-driven Streamlit buttons
  ↓
No browser-level page navigation
```

## Why this is more robust

```text
No dependency on the remaining viewport space to the right of a tab.
No dependency on Streamlit column overflow behavior for the dropdown width.
Long groups can use the full nav row.
All Data & Schemas tabs remain visible.
Labels can wrap instead of disappearing.
```

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
