# Phase 10 — Alerting, Ownership, and Incident Workflow

This phase turns incident analytics into an operational workflow.

## New workspace

```text
Incidents > Incident Workflow
```

## What it adds

```text
incident status
owner/team assignment
next action tracking
resolution summary
analyst notes
SLA state
triage queue
exportable incident report
```

## Local workflow store

By default, workflow state is stored in a configurable local JSON file:

```text
/app/data/incident_workflow.json
```

The path is configurable in:

```text
config/dashboard_performance.json
```

under:

```text
incident_workflow.store_path
```

This avoids requiring database migrations during the portfolio/demo phase.

## Configurable workflow options

```text
status_options
default_status
owner_options
severity_sla_minutes
escalation settings
report settings
```

## Exportable reports

The workspace can generate a Markdown incident report containing:

```text
incident metadata
current workflow state
owner
next action
resolution summary
analyst notes
recommended action
evidence JSON
```

## Production option

Optional SQL template:

```text
sql/phase10_incident_workflow.sql
```

This includes tables for:

```text
incident_workflow
incident_workflow_notes
```

The dashboard works without these tables.
