# Phase 13.13 — Form Control Containment Polish

This patch fixes inner controls spilling outside bordered cards/panels.

## Fixed

```text
Documentation audience badge stays inside the documentation side-nav border.
Demo Control Center number inputs stay inside their bordered cards.
Number input stepper buttons no longer push the field past the card edge.
Reset confirmation card keeps checkbox, button, and caption inside the border.
Action buttons respect parent card width.
```

## Root cause

Several Streamlit/BaseWeb controls were styled with `width: 100%` while also carrying padding, borders, or number-stepper controls. Without explicit `box-sizing: border-box` and `min-width: 0`, their visual width could exceed the parent panel.

## Implementation

Added a containment layer for:

```text
documentation side-nav badges
demo number input cards
BaseWeb number input internals
demo action buttons
reset confirmation card
checkbox/caption rows
future keyed Aegis widgets
```

The patch keeps the existing visual language while making the layout more robust.
