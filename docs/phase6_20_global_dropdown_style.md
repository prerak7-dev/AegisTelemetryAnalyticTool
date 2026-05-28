# Phase 6.20 — Global Dropdown Style

This patch applies the left-navigation dropdown typography and field styling to dropdowns/selectboxes across all dashboard workspaces.

## What changed

All `st.selectbox` / BaseWeb select fields now use:

```text
color: #25232a
font-size: 0.82rem
font-weight: 850
letter-spacing: 0.055em
text-transform: uppercase
square borders
light tab-like gradient background
white hover state
```

Open dropdown menus are also styled globally because BaseWeb renders popovers outside the local workspace DOM.

## Scope

This affects dropdown/select fields in:

```text
Operations
Incidents
Rules & Replay
Data & Schemas
Sidebar / left navigation
```
