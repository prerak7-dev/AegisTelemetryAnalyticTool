/*
Phase 10 — Incident Workflow

Optional ClickHouse table for production deployments.

The dashboard implementation uses a configurable local JSON store by default so
Phase 10 works without migrations. Production deployments can replace or mirror
that local workflow store with this table.
*/

CREATE TABLE IF NOT EXISTS incident_workflow
(
    incident_id String,
    status LowCardinality(String),
    assigned_owner String,
    next_action String,
    resolution_summary String,
    created_at DateTime,
    updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (incident_id);

CREATE TABLE IF NOT EXISTS incident_workflow_notes
(
    incident_id String,
    author String,
    note String,
    created_at DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(created_at)
ORDER BY (incident_id, created_at);

/*
Production note:

Keep local workflow store settings in config/dashboard_performance.json under
incident_workflow. If moving to ClickHouse, keep the same status/owner options
and report behavior so the dashboard and backend do not drift.
*/
