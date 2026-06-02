# Phase 13.17 — Number Input Stepper Containment Fix

This patch fixes the Demo Control Center number input controls.

## Fixed

```text
Duration Seconds input no longer touches/clips against the right card border.
Events Per Second input no longer touches/clips against the right card border.
Minus/plus steppers remain inside the input row.
The input row uses the card's padded content box correctly.
All number-input corners remain square.
```

## Root cause

Streamlit/BaseWeb number inputs render nested wrappers for:

```text
input text field
minus stepper
plus stepper
```

The outer widget was contained, but the inner flex row could still consume too much width and visually reach the card edge.

## Fix

The BaseWeb input row now uses an explicit contained flex model:

```text
text input: flexes
minus button: fixed 2rem
plus button: fixed 2rem
outer row: 100% of padded card content
overflow: hidden
box-sizing: border-box
```
