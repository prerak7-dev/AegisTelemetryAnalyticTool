# Phase 13.10 — Robust Horizontal Workspace Subnav

This patch replaces the experimental navigation styling with an isolated v2 navigation implementation.

## Root cause

The previous fixes were fighting old CSS and Streamlit DOM behavior at the same time. The result was inconsistent:

```text
some groups rendered horizontal
some groups rendered vertical
old CSS rules continued to affect new attempts
grid/flex overrides targeted the wrong Streamlit nesting level
```

## Fix

Phase 13.10 uses a new key namespace:

```text
aegis_v2_*
```

This prevents old `aegis_nav_*` CSS from affecting the new layout.

## Design rules

```text
Subnavs are always horizontal rows.
Compact subnavs align to the associated main tab.
Long or overflow-risk subnavs use the full dashboard nav-row width.
Large custom groups automatically create balanced horizontal rows.
No vertical list layout.
No internal scrollbar.
No side-nav overlap.
No per-workspace CSS changes when developers add/remove workspaces.
```

## Customization behavior

Developers can update:

```text
services/dashboard/workspaces.py
```

The navigation automatically recalculates:

```text
group width
subnav estimated width
viewport-safe full-row mode
balanced row count
tab widths
dropdown height
```

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
