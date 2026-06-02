# Phase 13.21 — Custom Stepper Visibility Fix

This patch fixes the custom Demo Control Center stepper visibility issues.

## Fixed

```text
The + sign is visible.
The input value is visible.
The input control height is no longer compressed.
The minus/plus controls remain inside the card.
The row remains square-edged and aligned.
```

## Root cause

The previous CSS forced the entire Streamlit column to the same fixed height as the input control. That left no room for the label plus the input field, so the numeric value was visually compressed/hidden.

The `+` button was also too narrow and could be clipped by nested Streamlit button wrappers.

## Fix

```text
The row aligns controls at the bottom.
The text/input column is auto-height.
Only the actual input and buttons have fixed control height.
Stepper button columns are widened.
The plus glyph uses a full-width plus character for better rendering.
```
