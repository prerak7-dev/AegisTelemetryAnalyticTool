# Phase 13.4 — Right-Aligned Long Subnav + Two-Row Fallback

This patch addresses long subnav groups such as Data & Schemas.

## Required behavior

```text
Small subnav:
  aligns from the associated main tab

Long subnav that would clip to the right:
  shifts left so the full dropdown aligns with the right edge of the dashboard content viewport

Subnav longer than the viewport:
  splits into two rows structurally, rather than hiding tabs or requiring zoom-out

Side nav:
  dropdown width is based on the dashboard nav row, so it does not overlap the left side navigation
```

## Implementation

The navigation renderer now detects long groups using the workspace registry.

Long groups are shifted left using the measured nav group weights:

```text
left = -previous_group_widths
width = full_nav_row_width
```

Long groups are also chunked into two rows at render time, so Streamlit does not need to wrap columns after the fact.

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
