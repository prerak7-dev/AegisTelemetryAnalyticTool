from __future__ import annotations

from pathlib import Path

REQUIRED_FILES = [
    "docs/toolkit/production_readiness/overview.md",
    "docs/toolkit/production_readiness/openapi_contracts.md",
    "docs/toolkit/production_readiness/observability.md",
    "docs/toolkit/production_readiness/kafka_retention_dlq.md",
    "docs/toolkit/production_readiness/clickhouse_partitioning.md",
    "docs/toolkit/production_readiness/load_testing.md",
    "docs/toolkit/production_readiness/deployment_checklist.md",
    "docs/toolkit/production_readiness/readiness_checklist.md",
    "openapi/collector.openapi.json",
    "infra/observability/prometheus.yml",
    "infra/observability/grafana/aegis_telemetry_dashboard.json",
    "tools/load_test_collector.py",
]

def test_required_production_readiness_files_exist() -> None:
    missing = [path for path in REQUIRED_FILES if not Path(path).exists()]
    assert missing == []
