# Phase 6.4 — Two-Tier Tab Navigation

This patch replaces the grouped dropdown navigation with a two-level tab bar inspired by studio/careers site navigation.

## Navigation structure

Top row:

```text
Operations | Incidents | Rules & Replay | Data & Schemas
```

Lower row changes based on the selected group:

```text
Operations:
  Command Center | Selected Server | Scaling Readiness

Incidents:
  Incident Dossier | Incident Timeline

Rules & Replay:
  Rule Testing | Recommendation Rules | Timeline Stages

Data & Schemas:
  Data Quality | Source Schemas
```

## UX changes

- Removed the extra navigation description block.
- Preserved the older sharp tab style.
- Added CSS-only hover/underline/fade transitions.
- Uses native Streamlit radio controls for stable performance during live refresh.
- No custom JavaScript.
