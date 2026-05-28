# Phase 6.12 — Final State-Driven Hover Navigation Fix

This patch fixes the issue where the subnavigation row stayed visible all the time and where subnavigation items needed two clicks.

## Root cause

Previous CSS targeted Streamlit wrapper structure through fragile sibling/container selectors. In the rendered app, those selectors did not reliably match the actual DOM, so the subnavigation remained visible.

## Fix

The CSS now targets the actual radio groups by accessibility label:

```css
div[role="radiogroup"][aria-label="Workspace group"]
div[role="radiogroup"][aria-label="Workspace"]
```

The whole `Workspace` radio widget wrapper is hidden by default and revealed only while hovering the primary group row or the subnav itself.

## One-click fix

Navigation now uses Streamlit radio callbacks:

```python
on_change=_set_active_workspace_from_group
on_change=_set_active_workspace_from_radio
```

This updates the active workspace immediately instead of needing a second click.

## Guarantees

- No HTML links.
- No hrefs.
- No query parameters.
- No browser-level navigation.
- State-driven workspace switching.
- Phase 6.8-style light hover subnavigation.
- Dark subnav text on white background.
- Selected subnav item uses only a blue underline.
- White SVG breadcrumb arrow.
