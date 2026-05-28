# Phase 7.2.2 — Sidebar Selectbox Format Function Fix

This patch fixes the dashboard startup error:

```text
Could not connect to ClickHouse yet: 'NoneType' object is not callable
```

## Cause

The persisted sidebar helper passed:

```python
format_func=None
```

into `st.sidebar.selectbox(...)`.

Some Streamlit versions attempt to call `format_func`, so passing `None` caused:

```text
'NoneType' object is not callable
```

## Fix

The helper now builds `selectbox_kwargs` and only includes `format_func` when it is actually provided.

```python
selectbox_kwargs = {
    "label": label,
    "options": options,
    "key": key,
}
if format_func is not None:
    selectbox_kwargs["format_func"] = format_func

return st.sidebar.selectbox(**selectbox_kwargs)
```

This preserves the auto-refresh filter persistence fix while removing the crash.
