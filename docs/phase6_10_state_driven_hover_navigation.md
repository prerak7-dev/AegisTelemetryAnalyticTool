# Phase 6.10 — State-Driven Hover-Style Navigation

This patch combines the desired hover/dropdown visual behavior with state-driven workspace switching.

## What changed

- No HTML links.
- No query parameters.
- No browser-level page navigation.
- Workspace switching uses native Streamlit radio widgets and session state.
- The subnavigation row is collapsed by default.
- Hovering over the primary nav area reveals the subnavigation.
- Moving out collapses the subnavigation.
- Subnav text is dark gray/black on the white background.
- Selected subnav item uses only a blue underline highlight.
- Breadcrumb separator uses a white SVG right-arrow.

## Note

Streamlit still reruns the script internally when widget state changes. That is normal Streamlit behavior. This patch avoids browser refresh/navigation and keeps the dashboard URL/page stable.
