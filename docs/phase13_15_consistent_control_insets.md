# Phase 13.15 — Consistent Control Inset System

This patch generalizes the Phase 13.14 audience-badge padding fix across similar UI controls.

## Fixed

The following controls now use consistent symmetric insets inside bordered panels:

```text
Documentation audience badge
Documentation section expanders
Documentation page navigation buttons
Demo Control Center number inputs
Demo reset checkbox row
Demo reset button
Demo reset caption
Demo action buttons
Sidebar refresh button
```

## Why

Several Streamlit/BaseWeb controls render with nested wrappers. If the visible inner widget is set to `width: 100%` while the parent has padding/borders, the inner control can touch or spill past the panel edge.

## Design rule

A shared inset is now used:

```css
--aegis-control-inset: 0.5rem;
```

Controls that live inside bordered cards use:

```css
width: calc(100% - (var(--aegis-control-inset) * 2));
margin-left: var(--aegis-control-inset);
margin-right: var(--aegis-control-inset);
box-sizing: border-box;
```

This makes similar UI areas visually consistent without per-widget manual tuning.
