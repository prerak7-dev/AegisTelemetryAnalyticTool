# Configuration Model

Most behavior is controlled by:

```text
config/dashboard_performance.json
```

Important sections:

| Section | Purpose |
|---|---|
| tables | Logical table names |
| feature_flags | Enable/disable dashboard features |
| cache_policies | Query cache TTLs |
| query_budgets_ms | Query budget diagnostics |
| pressure_budgets | Pressure score thresholds |
| baseline | Baseline/anomaly settings |
| build_regression | Build comparison metrics and thresholds |
| fix_validation | Control/treatment metrics and guardrails |
| incident_workflow | Statuses, owners, SLA, report behavior |
| demo_control_center | Scenario launch and reset behavior |
| analyst_toolkit | SQL templates, notebooks, exports |
| documentation_workspace | Documentation nav and docs root |

## Configuration helper

Dashboard code should access config through:

```python
from services.dashboard.performance_config import cfg_get
```

or focused helpers such as:

```python
baseline_cfg(...)
build_regression_cfg(...)
fix_validation_cfg(...)
incident_workflow_cfg(...)
demo_control_cfg(...)
analyst_toolkit_cfg(...)
documentation_cfg(...)
```

## Rule of thumb

Avoid hardcoding values in views when the value could reasonably vary by:

- game
- backend capacity
- telemetry source
- region
- map
- build
- platform
- live event mode
- studio workflow

Prefer configuration.
