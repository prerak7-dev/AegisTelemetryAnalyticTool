# Phase 6.17 — Selected Main-Tab Hover Text Fix

This patch fixes the selected main navigation tab hover state.

## Problem

When hovering over the selected main tab, the background became light while the text stayed white, making the label unreadable.

## Fix

The selected tab now behaves as follows:

```text
Normal selected state:
  dark background + white text

Hovered selected state:
  light background + dark gray/black text
```

The blue underline remains the selected/hover indicator.
