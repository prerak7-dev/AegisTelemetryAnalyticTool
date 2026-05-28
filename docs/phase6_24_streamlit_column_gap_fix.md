# Phase 6.24 — Streamlit Column Gap Fix

This patch fixes:

```text
StreamlitInvalidColumnGapError: The gap argument to st.columns must be "small", "medium", or "large". The argument passed was None.
```

## Fix

Changed:

```python
st.columns(len(group.workspace_keys), gap=None)
```

to:

```python
st.columns(len(group.workspace_keys), gap="small")
```

The existing CSS still visually compresses the subnavigation into a tight horizontal tab strip.
