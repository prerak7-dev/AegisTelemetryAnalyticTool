# Schemas, Rules, and Timeline Stages

## Source schemas

Source schemas allow telemetry from different games, engines, or services to be normalized into a common model.

Location:

```text
source_schemas/
```

Use this when incoming telemetry uses different field names or structures.

## Recommendation rules

Recommendation rules define how incidents are detected and what action is recommended.

Location:

```text
recommendation_rules/
```

Rules should define:

- condition
- severity
- likely driver
- recommendation
- evidence fields
- validation plan
- guardrail metrics

## Timeline stages

Timeline stages define how incident root-cause sequences are explained.

Location:

```text
timeline_stages/
```

Stages should be:

- rule-specific when possible
- configurable
- evidence-backed
- tolerant of missing signals

## Good rule design

A good rule should answer:

```text
What happened?
Why do we think it happened?
Who is impacted?
What should the team do next?
How do we validate the fix?
What guardrails must not regress?
```

## Avoid

- generic recommendations for every incident
- hardcoded one-size-fits-all thresholds
- root-cause stages that always appear even when evidence is absent
- recommendations without validation metrics
