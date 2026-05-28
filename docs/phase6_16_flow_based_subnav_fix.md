# Phase 6.16 — Flow-Based Subnav Fix

This patch removes absolute-positioned subnav placement.

## Why

The previous implementation used pixel-based `top` positioning. In Streamlit, wrapper heights can change depending on the rendered DOM, so the dropdown appeared below the breadcrumb/title area and created an unclickable gap.

## Fix

The subnav now expands in normal document flow directly under the hovered main tab.

This means:

- no hardcoded `top: 47px`
- no absolute positioning for the subnav
- no invisible hover bridge needed
- no cursor gap between main tab and subnav
- subnav remains clickable because it is directly adjacent to the top tab
- subnav still shrink-wraps to the final tab

## Behavior

Workspace switching remains state-driven:

- no links
- no hrefs
- no query parameters
- no browser-level navigation
