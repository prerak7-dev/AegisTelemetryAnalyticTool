# Phase 6.15 — Navigation Positioning and Clickability Fix

This patch fixes the visible gap between the primary nav and the hover subnav.

## Fixes

- The whole nav row is wrapped in `st.container(key="aegis_nav_bar")`.
- The nav bar is locked to `48px` height.
- Each group container is locked to `48px` height.
- The subnav is positioned at `top: 47px`, overlapping the main nav by 1px.
- A 12px invisible hover bridge prevents the subnav from closing while moving the cursor downward.
- The subnav shrink-wraps with `width: max-content` and ends at the final tab.
- Workspace switching remains Streamlit-state-driven.

## No browser navigation

This patch still uses:

- no links
- no hrefs
- no query parameters
- no browser-level navigation
