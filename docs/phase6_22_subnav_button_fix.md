# Phase 6.22 — Subnavigation Button Fix

This patch fixes the issue where clicking an already-selected subnavigation item inside an inactive main group did not change the workspace.

## Root cause

The subnavigation used one `st.radio` per group. If an inactive group already had its first/default item selected, clicking that same radio option did not fire `on_change`, because the radio value did not change.

## Fix

Subnavigation items are now Streamlit buttons instead of radios.

Buttons always fire when clicked, so clicking a group's default/current subnav item still updates:

```text
aegis_active_workspace_key
```

## Guarantees

- no links
- no hrefs
- no query parameters
- no browser-level navigation
- one-click workspace switching
- Phase 6.8-style light dropdown
- dark subnav text
- active item shown only with a blue underline
