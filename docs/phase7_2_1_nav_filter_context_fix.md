# Phase 7.2.1 — Navigation, Filter Persistence, and Data Context Fix

This patch fixes two usability issues and adds one analyst-quality improvement before the next phase.

## Fixed: Performance Config subnav outside viewport

Problem:

The `Data & Schemas` subnavigation had enough items that `Performance Config` could render outside the browser window at normal zoom.

Fix:

The subnavigation is now rendered as a full-width responsive row below the main navigation instead of inside the narrow rightmost group column.

The hover behavior is generated from the workspace registry, not hardcoded group names. If developers add or remove workspace groups, the hover rules are generated dynamically.

## Fixed: filters reset during auto refresh

Problem:

Sidebar selectboxes were rebuilt with `index=...` defaults on rerun, so live refresh could reset:

```text
source profile
region
server
analysis window
refresh interval
table row limit
```

Fix:

All sidebar controls now use stable `st.session_state` keys. A selected value only resets if it is no longer available in the current option list.

## Added: visible filtered data scope

A filter context strip now appears below the workspace navigation and before the KPI strip.

It shows:

```text
workspace
source profile
region
server
analysis window
table row limit
```

This makes it clearer what filtered data each chart/table is showing.

## Added: horizontal table scrolling

`render_table(...)` now wraps tables in a horizontal-scroll shell. Wide evidence tables can scroll horizontally instead of clipping columns.
