# Phase 13.8 — Customizable Adaptive Subnav Layout

This patch changes the workspace subnav architecture so it remains consistent when developers add or remove workspaces.

## Problem

The previous subnav implementation used manual row splitting and Streamlit column widths. That made the design fragile:

```text
5 tabs could become an uneven 3/2 layout
6 tabs depended on hand-authored 3/3 behavior
adding/removing workspaces could require another CSS/readjustment pass
label-length-based widths could create gaps or protruding tabs
```

## New approach

Subnavs are now adaptive flex panels:

```text
compact group:
  starts aligned with its main nav tab

long group:
  shifts to the dashboard content row edge

all groups:
  use adaptive flex items
  wrap automatically when needed
  stretch the last row to fill the available panel width
  avoid internal scrollbars
  preserve hover and active blue underline states
```

## Why this is more robust

The layout no longer depends on a fixed number of tabs or manual row rules.

Developers can add or remove workspace entries in:

```text
services/dashboard/workspaces.py
```

without also recalculating:

```text
row splits
tab widths
empty panel space
viewport clipping
```

## Implementation

The renderer now outputs subnav buttons sequentially.

CSS handles:

```text
wrapping
tab width
last-row stretching
hover underline
active underline
viewport-safe long group alignment
```

This makes the layout policy design-system driven instead of workspace-count driven.
