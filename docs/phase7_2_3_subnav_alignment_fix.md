# Phase 7.2.3 — Subnavigation Alignment Fix

This patch restores the working per-group hover subnavigation behavior.

## Fixed

The previous full-width responsive subnav removed the viewport overflow issue but reintroduced two older problems:

```text
gap between main nav and subnav
subnav tabs not selectable
```

## New behavior

Subnav rows are again rendered as direct children of their owning main group. This keeps the hover path continuous:

```text
main tab hover
  ↓
subnav appears directly below
  ↓
cursor moves into subnav without crossing a detached gap
  ↓
buttons remain clickable
```

## Viewport fix

Right-edge groups are now right-aligned through generated CSS. This means a group such as:

```text
Data & Schemas > Performance Config
```

extends leftward when needed instead of rendering outside the browser viewport.

The alignment is generated from the workspace registry, not by hardcoding the group label.
