# Phase 6.19 — Remove Top White Dashboard Strip

This patch removes the default Streamlit header/toolbar band that appeared as a white strip above the dashboard hero.

## What changed

The dashboard now hides:

```text
stHeader
stToolbar
stDecoration
MainMenu
footer
```

and forces the app shell/background to match the dashboard background:

```text
#34313d
```

It also removes the default top padding from the Streamlit main block container.
