# Phase 6.14 — Subnavigation Gap and Width Fix

This patch fixes two remaining hover-navigation layout issues.

## Issue 1: Subnav appears too far below the main tab

Cause:

Streamlit wraps markdown and radio widgets in extra block containers. The previous absolute-positioning rules placed the subnav relative to a wrapper whose effective height was larger than the visible tab.

Fix:

Each group container is now pinned to the exact primary-tab height:

```css
height: 48px;
min-height: 48px;
max-height: 48px;
```

The subnav is placed directly beneath the tab at `top: 47px`, with a small invisible hover bridge to prevent disappearing while moving the cursor downward.

## Issue 2: Empty white strip after the last subnav tab

Cause:

Streamlit stretched the radio wrapper/radiogroup to full width.

Fix:

The subnav now shrink-wraps to its contents:

```css
width: max-content;
min-width: max-content;
display: inline-flex;
```

The last tab also removes its right border so the subnav visually ends cleanly.

## State model

No navigation behavior changed:

- no links
- no hrefs
- no query parameters
- no browser-level navigation
- workspace switching remains Streamlit-state-driven
