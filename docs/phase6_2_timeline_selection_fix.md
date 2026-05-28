# Phase 6.2 — Incident Timeline Selection Fix

This patch fixes two Incident Timeline UX issues.

## Issue 1: Same three stages for every incident

Cause:

The Timeline stage profile selector sorted profiles alphabetically and defaulted to index `0`.

Since `custom_timeline_stages_example` alphabetically comes before `default_timeline_stages`, the dashboard selected the example profile by default. That example profile intentionally has only three stages:

```text
incident_starts
custom_boss_phase_begins
recommendation_triggers
```

Fix:

The Incident Timeline now defaults to:

```text
TIMELINE_STAGE_PROFILE=default_timeline_stages
```

or `default_timeline_stages` if the environment variable is missing.

## Issue 2: Selected incident changed during live refresh

Cause:

The incident selectbox used a label/options flow that could reset when new incidents were inserted at the top after refresh.

Fix:

Incident selection now uses stable `incident_id` values and Streamlit session state. The selected incident stays pinned across live refreshes as long as it is still in the current filter window.

A new optional checkbox is available:

```text
Auto-follow latest incident
```

When enabled, the selector intentionally follows the newest incident. It is off by default.
