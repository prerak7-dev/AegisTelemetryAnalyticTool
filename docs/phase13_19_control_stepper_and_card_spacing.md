# Phase 13.19 — Control Stepper and Card Spacing Polish

This patch fixes the Demo Control Center numeric controls and Command Center card spacing.

## Fixed: Demo numeric controls

The Duration Seconds and Events Per Second controls now use a custom contained stepper:

```text
numeric text input
minus button
plus button
```

This restores visible `- / +` controls without using Streamlit/BaseWeb's fragile native `number_input` stepper internals.

## Behavior

```text
Duration seconds:
  min 15
  max 3600
  step 15

Events per second:
  min 1
  max 5000
  step 10
```

Values are parsed, clamped, stored in session state, and passed to scenario command generation as integers.

## Fixed: Command Center card spacing

The Command Center pressure and metric cards now use clearer spacing so they read as individual cards instead of one large split-column panel.

Updated:

```text
pipeline metric card gaps
pressure card gaps
card bottom spacing
transparent column backgrounds
stronger card separation
```
