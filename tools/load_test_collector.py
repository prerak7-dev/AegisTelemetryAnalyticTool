from __future__ import annotations

import argparse
import json
import random
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

import requests

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def make_event(sequence: int, build_version: str) -> dict[str, Any]:
    region = random.choice(["eu-west", "us-east", "us-west", "south-america", "southeast-asia"])
    server_id = f"{region}-{random.randint(1, 24):03d}"
    return {
        "event_id": f"load_{uuid.uuid4().hex}",
        "event_time": utc_now_iso(),
        "source_profile": "aegis_default",
        "region": region,
        "server_id": server_id,
        "match_id": f"load-match-{random.randint(1, 50)}",
        "map_id": random.choice(["northern_ridge", "skybridge", "sunken_city"]),
        "zone_id": random.choice(["central", "north_gate", "market", "boss_arena"]),
        "build_version": build_version,
        "category": "gameplay",
        "event_type": random.choice(["movement_tick", "ability_cast", "aoe_ability_cast", "physics_event"]),
        "priority": random.choice([1, 1, 1, 2, 3]),
        "player_count": random.randint(20, 160),
        "players_nearby": random.randint(0, 140),
        "server_frame_ms": random.uniform(18, 75),
        "packet_loss_percent": random.uniform(0, 6),
        "packet_out_kbps": random.uniform(700, 6800),
        "replicated_objects": random.randint(80, 1500),
        "physics_events": random.randint(0, 80),
        "memory_mb": random.uniform(2500, 9200),
        "cpu_percent": random.uniform(25, 96),
        "sequence": sequence,
    }

def post_batch(url: str, events: list[dict[str, Any]], timeout: float) -> tuple[int, float, str]:
    start = time.perf_counter()
    try:
        response = requests.post(f"{url.rstrip('/')}/v1/events", json={"source_profile": "aegis_default", "events": events}, timeout=timeout)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return response.status_code, elapsed_ms, response.text[:300]
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return 0, elapsed_ms, str(exc)

def main() -> None:
    parser = argparse.ArgumentParser(description="AegisTelemetry collector load test profile")
    parser.add_argument("--collector-url", default="http://localhost:8000")
    parser.add_argument("--events-per-second", type=int, default=500)
    parser.add_argument("--duration-sec", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout-sec", type=float, default=5.0)
    parser.add_argument("--build-version", default="load-test")
    args = parser.parse_args()

    total_events = args.events_per_second * args.duration_sec
    total_batches = max(1, total_events // args.batch_size)

    print(json.dumps({
        "mode": "collector_load_test",
        "collector_url": args.collector_url,
        "events_per_second": args.events_per_second,
        "duration_sec": args.duration_sec,
        "batch_size": args.batch_size,
        "workers": args.workers,
        "target_events": total_events,
        "target_batches": total_batches,
    }, indent=2))

    latencies: list[float] = []
    status_counts: dict[int, int] = {}
    failures: list[str] = []
    sequence = 0
    batch_interval = args.batch_size / max(args.events_per_second, 1)
    next_submit = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = []
        for _ in range(total_batches):
            events = []
            for _ in range(args.batch_size):
                sequence += 1
                events.append(make_event(sequence, args.build_version))

            futures.append(pool.submit(post_batch, args.collector_url, events, args.timeout_sec))

            next_submit += batch_interval
            sleep_for = next_submit - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)

        for future in as_completed(futures):
            status, latency_ms, body = future.result()
            latencies.append(latency_ms)
            status_counts[status] = status_counts.get(status, 0) + 1
            if status < 200 or status >= 300:
                failures.append(f"{status}: {body}")

    latencies_sorted = sorted(latencies)
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95) - 1] if latencies_sorted else 0
    p99 = latencies_sorted[int(len(latencies_sorted) * 0.99) - 1] if latencies_sorted else 0

    result = {
        "submitted_batches": len(latencies),
        "submitted_events": len(latencies) * args.batch_size,
        "status_counts": status_counts,
        "latency_ms_avg": statistics.mean(latencies) if latencies else 0,
        "latency_ms_p95": p95,
        "latency_ms_p99": p99,
        "failures_sample": failures[:10],
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
