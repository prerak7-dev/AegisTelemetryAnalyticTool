# Dashboard Import Fix

If the dashboard reports:

```text
ModuleNotFoundError: No module named 'services'
```

the Streamlit process cannot see `/app` as a Python import root.

This patch fixes that by:

- adding `services/__init__.py`
- copying it into the dashboard image
- setting `PYTHONPATH=/app` in `services/dashboard/Dockerfile`

## Run

```bash
docker compose down --remove-orphans
docker compose up --build
```
