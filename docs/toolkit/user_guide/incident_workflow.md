# Incident Workflow

The Incident Workflow workspace turns detected incidents into operational follow-up.

## Workflow fields

| Field | Meaning |
|---|---|
| Status | open, investigating, mitigated, resolved, deferred |
| Assigned owner | Team or person responsible |
| Next action | The immediate follow-up action |
| Resolution summary | What fixed or closed the incident |
| Analyst notes | Investigation log |
| SLA state | within SLA, at risk, breached, resolved |

## Recommended triage process

```text
1. Open Incident Dossier
2. Pick high-confidence critical/warning incidents
3. Open Incident Workflow
4. Assign owner
5. Add next action
6. Add analyst notes
7. Export incident report
8. Mark resolved when fix is validated
```

## Exportable report

The report includes:

- incident metadata
- symptom
- player impact
- recommended action
- owner
- next action
- resolution summary
- analyst notes
- evidence JSON

Use it as a portfolio artifact or internal handoff document.
