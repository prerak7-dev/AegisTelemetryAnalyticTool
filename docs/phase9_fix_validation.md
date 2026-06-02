# Phase 9 — Experimentation and Fix Validation

This phase completes the analytics decision loop:

```text
Detect issue
Recommend action
Apply change
Validate impact
Monitor guardrails
```

## New workspace

```text
Rules & Replay > Fix Validation
```

## What it answers

```text
Did treatment improve p95 server frame?
Did packet-out decrease?
Did replication/physics pressure decrease?
Did packet loss/desync/rubberband guardrails regress?
Was the result statistically meaningful?
Is the fix VALIDATED / PROMISING / INCONCLUSIVE / REGRESSED / FAIL GUARDRAILS / LOW CONFIDENCE?
```

## Configuration

Settings live in:

```text
config/dashboard_performance.json
```

under:

```text
fix_validation
```

Configurable areas:

```text
experiment field names
default control/treatment variant names
minimum samples per variant
statistical test thresholds
primary improvement thresholds
guardrail regression tolerance
metric catalog
metric role: primary or guardrail
metric direction: lower_is_better or higher_is_better
metric weights
```

## Simulator support

Generate control and treatment traffic:

```bash
python simulator/generate_traffic.py \
  --scenario replication_overload \
  --build-version 0.2.1 \
  --experiment-id replication_radius_fix \
  --experiment-variant control \
  --fix-validation-mode control
```

```bash
python simulator/generate_traffic.py \
  --scenario replication_overload \
  --build-version 0.2.1 \
  --experiment-id replication_radius_fix \
  --experiment-variant treatment \
  --fix-validation-mode treatment_improved
```

Other modes:

```text
none
control
treatment_improved
treatment_regressed
treatment_guardrail_regressed
```

## Production template

Optional SQL table:

```text
sql/phase9_fix_validation.sql
```

The workspace works without this table by reading experiment fields from `raw_events.raw_json`.
