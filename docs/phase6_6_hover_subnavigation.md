# Phase 6.6 — Hover-Expanded Workspace Subnavigation

This patch replaces the always-visible lower subnavigation row with a hover-expanded subnavigation bar.

## Behavior

- Top-level workspace groups are always visible.
- Hovering over a group reveals its sub-workspaces.
- Moving outside the group/subnav collapses the subnavigation automatically.
- Clicking a sub-workspace updates the `workspace` query parameter.
- No custom JavaScript is used.

## Workspace title

The workspace region now shows a breadcrumb-style title:

```text
Operations [separator image] Command Center
```

The separator image is loaded from:

```text
services/dashboard/assets/breadcrumb_separator.png
```

A text fallback is used if the image is missing.
