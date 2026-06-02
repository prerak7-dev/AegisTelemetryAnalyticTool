# Phase 13.16 — Global Design System Hardening

This patch adds an application-wide design-system consistency layer.

## Fixed

```text
No rounded corners anywhere in app controls
No one-sided rounded BaseWeb input corners
Documentation audience badge has balanced left/right inset
Documentation nav buttons have balanced inset
Documentation section descriptions have balanced inset
Demo number inputs stay inside bordered cards
Number input stepper buttons stay contained
Reset checkbox, reset button, and caption align to the same inset
Buttons cannot spill beyond card borders
Future Aegis keyed controls inherit defensive containment
```

## Root cause

The previous patches fixed isolated controls, but Streamlit and BaseWeb inject nested wrappers with their own widths, padding, borders, and border-radius rules. That caused inconsistent behavior:

```text
one-sided rounded corners
inputs touching one panel edge
buttons wider than their cards
badges using full width plus padding
stepper controls pushing number inputs outside the border
```

## Design rule

The app now enforces:

```text
square edges
box-sizing: border-box
max-width: 100%
min-width: 0
single source of inner inset
contained BaseWeb input internals
consistent card padding
```

Shared variables:

```css
--aegis-control-inset: 0.75rem;
--aegis-control-height: 2.75rem;
```

This gives the app a consistent, sharp, premium dashboard language across current and future controls.
