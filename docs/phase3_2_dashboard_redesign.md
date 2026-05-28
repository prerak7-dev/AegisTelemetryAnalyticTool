# Phase 3.2 — Dashboard Visual Redesign

This patch focuses on presentation quality and readability.

## Design goals

- No rounded components
- Sharp editorial layout
- Better contrast and clearer hierarchy
- More premium charts and easier-to-read tables
- Visual inspiration from the provided Guerrilla careers screenshot

## Main changes

1. Replaced the previous rounded dossier/folder look with a sharp rectilinear system.
2. Updated the palette to a dark slate background with light utility cards and stronger contrast.
3. Replaced `st.line_chart` views with styled Altair charts.
4. Standardized table height and presentation via a shared `render_table` helper.
5. Kept the existing functionality and filters unchanged.

## Run

```bash
docker compose down -v --remove-orphans
docker compose up --build
```
