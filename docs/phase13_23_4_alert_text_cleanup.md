# Phase 13.23.4 — Alert Text Theme + Runtime Notice Cleanup

This patch updates dashboard visual consistency after the Phase 13.23 runtime/query work.

## Fixed

```text
All Streamlit alert/info/warning/error text now uses grayish-white text.
Alert SVG/icon color is also normalized.
Alert boxes keep square edges and theme-matched borders.
```

## Removed

```text
Sidebar "Refresh policy: live · auto · Ns effective interval" caption
Sidebar "Live refresh paused..." policy caption
Command Center Phase 13.23 snapshot notice callout
```

## Updated files

```text
services/dashboard/styles.py
services/dashboard/sidebar.py
services/dashboard/views/command_center.py
```
