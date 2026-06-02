# Validation and Analyst Exports

## Baseline Intelligence

Use this when static thresholds are not enough.

Example:

```text
Normal EU-West northern_ridge p95 frame: 28 ms
Current p95 frame: 71 ms
Deviation: +153%
Severity: critical
```

## Build Regression

Use this for release readiness.

Questions:

- Did p95 server frame regress?
- Did packet out increase?
- Which map/zone regressed?
- Which source profile observed the regression?
- Is the candidate build PASS, WATCH, BLOCK, or LOW CONFIDENCE?

## Fix Validation

Use this to validate whether a recommendation worked.

Flow:

```text
Control: old behavior
Treatment: optimized behavior
Compare primary metrics
Check guardrails
Decide validated / promising / regressed / fail guardrails
```

## Analyst Toolkit

Use this for deeper investigation.

It provides:

- SQL template execution
- CSV export
- JSON export
- downloadable notebooks
- reusable SQL templates

Recommended analyst path:

```text
Run dashboard scenario
  ↓
Find incident or anomaly
  ↓
Export SQL evidence
  ↓
Open notebook
  ↓
Analyze deeper
  ↓
Attach findings to Incident Workflow
```
