# Phase 13.9 — Horizontal Adaptive Subnav Grid

This patch keeps the customizable navigation model but prevents subnav tabs from becoming a vertical single-column list.

## Design rules

```text
Subnav tabs are always horizontal grid items.
Compact groups align from their main tab.
Long/right-side groups shift to the dashboard content-row edge.
If the tab group is too wide, it wraps into additional horizontal rows.
The last row stretches to fill the panel.
No manual row splitting is required.
No per-workspace design recalibration is required.
```

## Why Phase 13.8 failed visually

Phase 13.8 rendered buttons sequentially, but Streamlit's default vertical block behavior could still stack those buttons vertically if the flex override did not bind to the correct DOM level.

## Fix

The subnav inner Streamlit block is now forced into CSS grid:

```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(...));
```

Each workspace button becomes a grid cell.

This keeps the layout customizable and horizontal while still allowing wrapping when the viewport requires it.

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
