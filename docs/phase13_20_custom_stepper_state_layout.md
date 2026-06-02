# Phase 13.20 — Custom Stepper State + Layout Fix

This patch fixes the Demo Control Center custom numeric stepper.

## Fixed

```text
No StreamlitAPIException from writing to a widget key after creation.
Duration Seconds minus/plus buttons stay fully visible.
Events Per Second minus/plus buttons stay fully visible.
The custom stepper remains square-edged and contained inside the card.
```

## Root cause

The custom stepper used the same session-state key for:

```text
the text input widget
the canonical parsed integer value
```

Streamlit does not allow modifying the same key after the widget has been instantiated.

## Fix

The control now uses two state keys:

```text
canonical value key:
  aegis_demo_duration_sec_text

widget input key:
  aegis_demo_duration_sec_text_input
```

The parsed canonical value can safely update after the widget renders because it is not the widget key.

The `- / +` callbacks update both keys before the widget is instantiated on rerun.

## Layout fix

The stepper row now uses:

```text
text field column: flexible
minus column: fixed 2.25rem
plus column: fixed 2.25rem
```

This prevents the plus control from clipping or disappearing at the right edge.
