# Phase 13.12 — Hierarchical Documentation Side Navigation

This patch updates the Documentation workspace navigation.

## Changed

The old documentation controls used:

```text
section dropdown
page radio selection
```

The new documentation workspace uses:

```text
hierarchical expanding side navigation
section expanders
state-driven page buttons
active page highlight
hover highlight
theme-matched dark side panel
```

## Why

The Documentation workspace should feel like professional product documentation, not a form with dropdowns.

The new side navigation is inspired by common product/project sidebars:

```text
Section
  Page
  Page
  Page

Section
  Page
  Page
```

## Customization

The hierarchy still comes from:

```text
config/documentation_navigation.json
```

Developers can add, remove, or reorder documentation sections and pages without changing view code.

## Updated files

```text
services/dashboard/views/documentation.py
services/dashboard/styles.py
```
