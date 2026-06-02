# Phase 13.1 — Subnav Viewport Alignment Fix

This patch fixes the Data & Schemas subnavigation clipping off the right side of the browser window.

## Root cause

After adding more workspaces under Data & Schemas, the subnav row became wider than the remaining viewport space when left-aligned from the main group tab.

## Fix

Navigation alignment is now registry-driven:

```text
Right-align subnav when:
- the group is near the right side of the nav row
- the group has many workspace tabs
- the estimated subnav width is above a safe threshold
```

This avoids hardcoding only `Data & Schemas` while still fixing the current issue.

## Behavior

```text
Short groups near the left side:
  subnav opens left-aligned from the group tab

Long groups or right-edge groups:
  subnav opens right-aligned from the group tab

If a future group is still wider than the viewport:
  subnav remains horizontal and scrolls instead of clipping
```

## Updated files

```text
services/dashboard/navigation.py
services/dashboard/styles.py
```
