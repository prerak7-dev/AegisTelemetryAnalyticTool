# Phase 13.5 — Two-Row Subnav Visual Polish

This patch keeps the two-row subnav implementation but fixes the visual issues.

## Fixed

```text
No scrollbar inside the subnav
No clipped second row
Consistent row height
Consistent button spacing
Blue underline restored on hover
Blue underline preserved for the active subnav tab
Readable text alignment
```

## Why this was needed

The Phase 13.4 two-row implementation successfully made all tabs reachable, but the visual container height and older overflow rules allowed the second row to be partially clipped and produced a scrollbar.

## Implementation

The patch adds explicit visual constraints for:

```text
subnav outer container
subnav rows
Streamlit horizontal blocks
Streamlit columns
button containers
subnav buttons
hover state
active state
scrollbar hiding
```

The dropdown now opens as a clean two-row panel with no visible internal scroll.
