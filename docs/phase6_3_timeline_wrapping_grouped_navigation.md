# Phase 6.3 — Timeline Wrapping, Contrast, and Grouped Navigation

This patch improves Incident Timeline readability and dashboard navigation.

## Incident Timeline readability

The root-cause sequence is now rendered as wrapped cards instead of only a Streamlit dataframe.

Each card shows:

```text
stage id
time
mode
matched / not observed
stage title
full wrapped details
```

The original dataframe remains available under:

```text
Root-cause sequence table
```

Low-contrast Streamlit blue caption/link text is forced to white in the Incident Timeline area.

## Grouped workspace navigation

The flat workspace tab row is replaced with grouped dropdown navigation.

Groups:

```text
Operations
  Command Center
  Selected Server
  Scaling Readiness

Incidents
  Incident Dossier
  Incident Timeline

Rules & Replay
  Rule Testing
  Recommendation Rules
  Timeline Stages

Data & Schemas
  Data Quality
  Source Schemas
```

## Performance

The grouped navigation uses native Streamlit selectboxes and CSS transitions only. No custom JavaScript is used, so live refresh remains stable and efficient.
