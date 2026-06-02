# Phase 13.18 — Demo Number Input Final Containment

This patch resolves the clipped `- / +` stepper issue in the Demo Control Center.

## Fixed

```text
Duration Seconds control no longer clips at the right edge.
Events Per Second control no longer clips at the right edge.
No fragile minus/plus stepper internals remain.
Controls stay square, contained, and visually consistent.
Values are still parsed as integers and bounded to valid ranges.
```

## Why this approach

Streamlit/BaseWeb number inputs render nested stepper controls that can visually overflow or clip depending on the internal DOM and browser width. Previous CSS containment still could not reliably control those internal stepper wrappers.

## Final approach

The Demo Control Center now uses numeric text inputs for these two fields:

```text
Duration seconds
Events per second
```

The values are parsed and clamped in Python:

```text
duration: 15 to 3600
events per second: 1 to 5000
```

This removes the unstable stepper layout while preserving the dashboard workflow and command generation behavior.
