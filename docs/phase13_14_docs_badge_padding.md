# Phase 13.14 — Documentation Badge Inner Padding Fix

This patch refines the Documentation workspace audience badge.

## Fixed

The audience badge no longer touches the right edge of the documentation side-nav panel.

## Change

The badge now uses symmetric inset spacing:

```text
left margin: 0.5rem
right margin: 0.5rem
width: calc(100% - 1rem)
```

This keeps the badge visually balanced inside the bordered panel.
