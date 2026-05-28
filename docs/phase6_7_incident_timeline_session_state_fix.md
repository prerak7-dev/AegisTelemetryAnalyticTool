# Phase 6.7 — Incident Timeline Session State Warning Fix

This patch removes the Streamlit warning:

```text
The widget with key "incident_timeline_selected_stage_profile" was created with a default value but also had its value set via the Session State API.
```

## Cause

The Incident Timeline set:

```python
st.session_state["incident_timeline_selected_stage_profile"] = ...
```

and also used the same key in:

```python
st.selectbox(..., key="incident_timeline_selected_stage_profile", index=...)
```

Streamlit warns when a widget key is both manually assigned and given a default value.

## Fix

The profile selector now uses:

```python
PROFILE_SESSION_KEY = "incident_timeline_selected_stage_profile"
PROFILE_WIDGET_KEY = "incident_timeline_stage_profile_widget"
```

The widget owns its widget key, and the app stores the selected value separately after the widget renders.
