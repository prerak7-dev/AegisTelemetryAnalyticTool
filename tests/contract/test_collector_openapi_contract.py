from __future__ import annotations

import json
from pathlib import Path

CONTRACT_PATH = Path("openapi/collector.openapi.json")

def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

def test_contract_file_exists() -> None:
    assert CONTRACT_PATH.exists()

def test_required_collector_paths_are_documented() -> None:
    contract = load_contract()
    paths = contract["paths"]

    assert "/health" in paths
    assert "/metrics" in paths
    assert "/v1/source-profiles" in paths
    assert "/v1/events" in paths
    assert "/v1/events/{source_profile}" in paths

def test_ingestion_result_schema_has_operational_counters() -> None:
    contract = load_contract()
    schema = contract["components"]["schemas"]["IngestionResult"]
    props = schema["properties"]

    for field in ["accepted", "failed", "sampled_or_dropped", "mapped", "validation_errors"]:
        assert field in props

def test_metrics_endpoint_is_prometheus_text() -> None:
    contract = load_contract()
    metrics_response = contract["paths"]["/metrics"]["get"]["responses"]["200"]
    assert "text/plain" in metrics_response["content"]

def test_openapi_version_and_title_are_stable() -> None:
    contract = load_contract()
    assert contract["openapi"].startswith("3.")
    assert contract["info"]["title"] == "AegisTelemetry Collector API"
