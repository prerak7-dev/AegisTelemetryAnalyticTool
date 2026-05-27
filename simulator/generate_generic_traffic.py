from __future__ import annotations

import argparse
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import requests

REGIONS = ["EU-West", "NA-East", "NA-West", "Japan", "Australia"]
ZONES = ["northern_ridge", "market_square", "central_lane", "river_delta"]
ABILITIES = ["rifle_burst", "aoe_fire_burst", "aoe_storm_pulse", "dash"]

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

def generate_generic_event(sequence_id: int, meltdown: bool = True) -> dict[str, Any]:
    region = random.choice(["EU-West", "NA-East"]) if meltdown and random.random() < 0.75 else random.choice(REGIONS)
    zone = "northern_ridge" if meltdown and region in {"EU-West", "NA-East"} and random.random() < 0.72 else random.choice(ZONES)
    shard = f"{region.lower().replace('-', '_')}_generic_{random.randint(1, 3) if zone == 'northern_ridge' else random.randint(4, 40):03d}"

    nearby = random.randint(20, 80)
    player_count = random.randint(50, 160)
    cpu = random.uniform(35, 70)
    frame = random.uniform(18, 40)
    packet_loss = random.uniform(0, 2)
    replicated = random.randint(1200, 7000)
    physics = random.randint(0, 25)
    event_name = random.choice(["combat.ability_cast", "server.frame", "network.sample", "replication.sample"])
    ability = random.choice(ABILITIES)

    if meltdown and region in {"EU-West", "NA-East"} and zone == "northern_ridge":
        nearby += random.randint(75, 170)
        player_count += random.randint(80, 200)
        cpu += random.uniform(20, 35)
        frame += random.uniform(22, 70)
        packet_loss += random.uniform(1.5, 6.0)
        replicated += random.randint(8000, 23000)
        physics += random.randint(50, 180)
        event_name = "combat.aoe_cast"
        ability = random.choice(["aoe_fire_burst", "aoe_storm_pulse"])

    return {
        "id": str(uuid.uuid4()),
        "ts": utc_now_iso(),
        "typeGroup": "combat" if event_name.startswith("combat") else "server",
        "name": event_name,
        "severityPriority": 1 if "aoe" in event_name else 2,
        "regionName": region,
        "shardId": shard,
        "activityId": f"{shard}-activity",
        "world": {
            "map": "storm_front",
        },
        "location": {
            "zone": zone,
            "x": random.uniform(-2000, 2000),
            "y": random.uniform(-2000, 2000)
        },
        "clientBuild": "generic-1.0.0",
        "population": {
            "serverPlayers": int(clamp(player_count, 0, 600)),
            "nearbyPlayers": int(clamp(nearby, 0, 340))
        },
        "gameplay": {
            "ability": ability
        },
        "perf": {
            "cpuPct": round(clamp(cpu, 0, 100), 2),
            "memMb": round(random.uniform(2600, 7600), 2),
            "frameMs": round(clamp(frame, 4, 180), 2)
        },
        "net": {
            "packetLossPct": round(clamp(packet_loss, 0, 20), 2),
            "outKbps": round(random.uniform(400, 9800), 2),
            "replicatedObjects": int(clamp(replicated, 0, 40000))
        },
        "impact": {
            "desyncs": random.randint(0, 3) if frame > 65 or packet_loss > 5 else 0,
            "rubberbands": random.randint(0, 5) if frame > 50 else 0
        },
        "physics": {
            "events": int(clamp(physics, 0, 600))
        },
        "ai": {
            "activeAgents": random.randint(40, 260) if meltdown else random.randint(5, 80),
            "pathRequests": random.randint(40, 700) if meltdown and random.random() < 0.25 else random.randint(0, 90)
        },
        "matchmaking": {
            "queueLength": random.randint(0, 400) if region == "EU-West" and random.random() < 0.10 else 0
        }
    }

def send_batch(collector_url: str, batch: list[dict[str, Any]]) -> None:
    url = collector_url.rstrip("/") + "/v1/events/generic_live_service"
    response = requests.post(url, json=batch, timeout=10)
    if response.status_code >= 400:
        print(f"Collector returned {response.status_code}: {response.text[:1000]}")
    response.raise_for_status()

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate generic live-service telemetry using a non-Aegis source schema.")
    parser.add_argument("--collector-url", default="http://localhost:8000")
    parser.add_argument("--events-per-second", type=int, default=500)
    parser.add_argument("--duration-sec", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument("--normal", action="store_true", help="Disable meltdown behavior")
    args = parser.parse_args()

    sequence_id = 0
    start = time.time()
    next_tick = start

    while time.time() - start < args.duration_sec:
        batch = []
        for _ in range(args.batch_size):
            sequence_id += 1
            batch.append(generate_generic_event(sequence_id, meltdown=not args.normal))

        send_batch(args.collector_url, batch)
        expected_batches_per_sec = max(args.events_per_second / args.batch_size, 1)
        next_tick += 1.0 / expected_batches_per_sec
        sleep_for = next_tick - time.time()
        if sleep_for > 0:
            time.sleep(sleep_for)

        if sequence_id % (args.batch_size * 10) == 0:
            print(f"sent_generic_events={sequence_id}")

    print(f"complete sent_generic_events={sequence_id}")

if __name__ == "__main__":
    main()
