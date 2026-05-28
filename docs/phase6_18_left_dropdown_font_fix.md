# Phase 6.18 — Left Navigation Dropdown Font Fix

This patch updates the left/sidebar dropdown styling so it matches the workspace tab typography.

## What changed

Sidebar dropdowns now use:

```text
color: #25232a
font-size: 0.82rem
font-weight: 850
letter-spacing: 0.055em
text-transform: uppercase
sharp square borders
light tab-like background
```

The opened dropdown menu popover is also styled globally because BaseWeb renders select dropdown popovers outside the sidebar DOM.
