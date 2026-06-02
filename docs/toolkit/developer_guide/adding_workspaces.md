# Adding Workspaces

## 1. Create a view file

Create:

```text
services/dashboard/views/my_workspace.py
```

Minimum structure:

```python
from __future__ import annotations

import streamlit as st

from services.dashboard.context import DashboardContext

def render(context: DashboardContext) -> None:
    st.subheader("My Workspace")
    st.write("Workspace content")
```

## 2. Register it

Edit:

```text
services/dashboard/workspaces.py
```

Add import:

```python
from services.dashboard.views import my_workspace
```

Add workspace:

```python
Workspace("my_workspace", "My Workspace", my_workspace.render)
```

Add it to a group:

```python
workspace_keys=("existing_workspace", "my_workspace")
```

## 3. Use context filters

Every workspace receives:

```python
DashboardContext
```

Use:

```python
context.filters.time_filter
context.active_filter
context.source_filter
context.region_filter
context.server_filter
```

This keeps workspace queries aligned with the sidebar filters.

## 4. Use query helpers

Prefer:

```python
query_df_named(...)
```

so Query Performance can track:

- query name
- duration
- budget
- rows
- errors

## 5. Keep the view configurable

For thresholds or table names, use:

```python
table_name(...)
cfg_get(...)
```

Do not hardcode values that belong in `dashboard_performance.json`.
