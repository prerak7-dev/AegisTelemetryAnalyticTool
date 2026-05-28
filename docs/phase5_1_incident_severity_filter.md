# Phase 5.1 — Incident Dossier Severity Filter

This patch adds analyst-facing severity filtering to the Incident Dossier.

## What changed

The Incident Dossier now includes an `Incident severity` selector:

```text
All severities
Critical only
Warnings only
```

The view also shows a small severity distribution table for the selected source profile, region, server, and time window.

## Why this matters

Analysts can now triage warning-level incidents separately from critical incidents without changing source, region, server, or time-window filters.
