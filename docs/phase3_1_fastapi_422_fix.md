# Phase 3.1 FastAPI 422 Fix

If the simulator fails with:

```text
422 Client Error: Unprocessable Entity for url: http://localhost:8000/v1/events
```

the collector endpoint is rejecting the request before it reaches Kafka.

This patch explicitly marks the `payload` parameter as the JSON request body:

```python
from fastapi import Body

def ingest(payload: Any = Body(...), ...):
    ...
```

It also updates simulator scripts to print the collector response body on HTTP errors, making future API debugging easier.

## Run

```bash
docker compose down
docker compose up --build
```

Then rerun the simulator:

```bash
cd simulator
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 200 --duration-sec 180
```
