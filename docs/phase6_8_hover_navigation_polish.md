# Phase 6.8 — Hover Navigation Polish

This patch fixes three hover-navigation issues.

## Fixes

### 1. Subnavigation text contrast

Subnavigation links now use dark gray/black text across all states:

```text
#3f3d45
```

The selected subnavigation item keeps the same text color and is indicated only by the blue underline.

### 2. Breadcrumb separator

The breadcrumb now uses a clean white SVG right arrow:

```text
services/dashboard/assets/breadcrumb_arrow.svg
```

The previous uploaded image asset is no longer used as the breadcrumb separator.

### 3. Same-tab navigation

Subnavigation links now include:

```html
target="_self"
```

Clicking a subnavigation item updates the current dashboard tab instead of opening a new browser tab.
