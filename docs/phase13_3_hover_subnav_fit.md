# Phase 13.3 — Hover-Stable Viewport-Fit Subnav

This patch replaces the failed full-layer hover approach with a hover-stable per-group subnav that can still shift to the nav-content edge when needed.

## Intended behavior

```text
Small subnav width:
  start of the subnav aligns with the associated main tab

Subnav would overflow viewport when aligned to main tab:
  subnav shifts left to the main nav content edge

Subnav wider than available content area:
  subnav wraps to two rows instead of hiding tabs

Subnav must not overlap the side nav:
  long subnav width is calculated from the dashboard content nav row, not from the full browser viewport
```

## Why Phase 13.2 failed

Phase 13.2 moved subnavs into a full overlay layer and relied on CSS `:has()` to reveal the row for the hovered main tab. In this Streamlit DOM, that selector path did not reliably match the rendered hover state, so no subnav appeared.

## Fix

Subnavs are again rendered as children of their main group, so hover works reliably.

Dynamic CSS now calculates:

```text
main group column width
previous group widths
total nav row width
```

For long/right-side groups, it shifts the subnav left by the previous group width and gives it the full nav-row width.

For very narrow screens, the subnav can wrap to two rows.

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
