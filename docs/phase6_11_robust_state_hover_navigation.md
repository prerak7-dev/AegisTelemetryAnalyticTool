# Phase 6.11 — Robust State-Driven Hover Navigation

This patch fixes the issue where the subnavigation row remained visible all the time.

## Root cause

The previous CSS relied on fragile sibling selectors between separate Streamlit elements. Streamlit wraps markdown and widgets in its own DOM containers, so the hide/show rule did not always match the actual rendered structure.

## Fix

The navigation now renders both rows inside a keyed Streamlit container:

```python
st.container(key="aegis_nav_hover_region")
```

It also places invisible marker elements before each radio widget:

```html
<div class="aegis-nav-primary-marker"></div>
<div class="aegis-nav-sub-marker"></div>
```

CSS targets those markers with `:has(...)` to reliably identify:

- the primary group radio
- the sub-workspace radio

## Behavior

- Top group row is always visible.
- Subnavigation is hidden by default.
- Subnavigation appears only while the top navigation container is hovered.
- Moving outside collapses the subnavigation.
- Workspace switching is still Streamlit-state-driven.
- No links, no hrefs, no query parameters, and no browser-level navigation.

## Styling

The subnavigation uses the Phase 6.8 visual language:

- light dropdown strip
- dark gray/black text
- selected item indicated only by blue underline
- white SVG breadcrumb arrow
