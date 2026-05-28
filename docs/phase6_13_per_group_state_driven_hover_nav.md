# Phase 6.13 — Per-Group State-Driven Hover Navigation

This patch fixes the two remaining navigation issues.

## Fixes

- Hovering over any main group now reveals that group’s own subnavigation.
- The subnavigation remains open while moving the cursor from the group tab into the dropdown.
- Subnav items are real Streamlit radio widgets, so workspace switching remains state-driven.
- No links, hrefs, query parameters, or browser-level navigation are used.

## Styling

The dropdown keeps the Phase 6.8 visual language:

- light dropdown strip
- dark gray/black subnav text
- selected subnav indicated only by a blue underline
- white SVG breadcrumb arrow
