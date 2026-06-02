# Phase 13.11 — Dynamic Compact Subnav Width

This patch refines the Phase 13.10 navigation system.

## Fixed

Small subnav groups no longer expand to the full nav-row width.

Example:

```text
Demo
  Demo Control Center
```

The Demo subnav now stays compact because it only has one option.

## Policy

```text
1-2 subnav options:
  compact width based on option labels
  if near the right edge, right-align to the main tab
  never expand to full nav-row width

larger or overflow-risk groups:
  use full dashboard nav-row width
  automatically create balanced horizontal rows when needed
```

## Why this is better for customization

Developers can add or remove workspaces without tuning CSS:

```text
small groups remain compact
long groups remain viewport-safe
right-edge small groups do not become oversized
```

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
