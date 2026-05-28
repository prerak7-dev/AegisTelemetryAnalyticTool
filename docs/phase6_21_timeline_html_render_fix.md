# Phase 6.21 — Incident Timeline HTML Render Fix

This patch fixes raw HTML appearing under the Incident Timeline root-cause sequence.

## Problem

The previous renderer built one large HTML string by joining all timeline cards and sent it to:

```python
st.markdown("".join(cards), unsafe_allow_html=True)
```

In some Streamlit/Markdown render cycles, especially during reruns or live refresh, later cards could be displayed as escaped raw HTML.

## Fix

The root-cause sequence renderer now renders each card independently:

```python
st.markdown(card_html, unsafe_allow_html=True)
```

This is more reliable because each stage card is a complete HTML block and Streamlit does not need to parse one large concatenated block.

## Files changed

```text
services/dashboard/components.py
services/dashboard/styles.py
```
