# Phase 6.5 — Distinct Sub-Navigation Styling

This patch makes the two-tier workspace navigation hierarchy clearer.

## What changed

The top row remains the primary group navigation:

```text
Operations | Incidents | Rules & Replay | Data & Schemas
```

The second row is now visually distinct as sub-navigation:

- smaller tab scale
- inset secondary strip
- left accent bar
- subtle `Sub-navigation / Active Group` label
- lighter background
- active sub-tab uses an inset underline instead of the primary dark selected state

## Why

Previously both rows looked almost identical, so it was not immediately clear that the lower row was subordinate to the selected group.
