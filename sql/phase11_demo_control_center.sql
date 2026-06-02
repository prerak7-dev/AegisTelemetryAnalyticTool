/*
Phase 11 — Demo Control Center

Optional production table for recording scenario launches. The dashboard works
without this table by using a local JSON history store.
*/

CREATE TABLE IF NOT EXISTS demo_scenario_history
(
    created_at DateTime,
    scenario_id String,
    command_label String,
    command String,
    pid UInt64,
    launch_mode LowCardinality(String),
    user_label String DEFAULT 'local'
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(created_at)
ORDER BY (created_at, scenario_id, command_label);

/*
Production note:

The demo scenario library is configured in config/demo_scenarios.json and
config/dashboard_performance.json under demo_control_center.
*/
