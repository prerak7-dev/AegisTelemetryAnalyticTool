# OpenAPI Contracts and Contract Tests

## Collector contract

The collector API contract is stored at:

```text
openapi/collector.openapi.json
```

It documents:

- `GET /health`
- `GET /metrics`
- `GET /v1/source-profiles`
- `POST /v1/events`
- `POST /v1/events/{source_profile}`

## Why this matters

The collector is the boundary between telemetry producers and the analytics platform. A stable contract allows:

- simulator clients to stay compatible
- game clients/services to integrate safely
- tests to catch accidental breaking changes
- documentation to stay aligned with implementation

## Contract test files

```text
tests/contract/test_collector_openapi_contract.py
tests/contract/test_production_docs_inventory.py
```

Run:

```bash
pytest tests/contract
```

## Contract review checklist

Before changing the collector API:

- Is the endpoint documented in OpenAPI?
- Is the response schema updated?
- Are validation errors documented?
- Are path/query parameters explicit?
- Are contract tests updated?
- Are simulator clients still compatible?
- Is the documentation workspace updated?

## API compatibility rule

Breaking changes should be versioned. Prefer adding optional fields over renaming required fields.
