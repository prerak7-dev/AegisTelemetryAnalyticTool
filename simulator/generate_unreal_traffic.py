from __future__ import annotations

import argparse
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import requests

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def generate_unreal_event(sequence_id: int) -> dict[str, Any]:
    region = random.choice(["EU-West", "NA-East"])
    hot = random.random() < 0.70
    server_id = f"{region.lower()}-ue-ds-{random.randint(1, 4) if hot else random.randint(5, 50):03d}"
    zone = "northern_ridge" if hot else random.choice(["river_delta", "market_square", "skybridge"])
    event_name = "Gameplay.AoEAbilityCast" if hot else random.choice(["Server.FrameSample", "Net.DriverSample", "Gameplay.AbilityCast"])

    frame = random.uniform(55, 130) if hot else random.uniform(16, 38)
    packet_loss = random.uniform(1.5, 8.0) if hot else random.uniform(0.0, 1.8)
    replicated = random.randint(10000, 32000) if hot else random.randint(1000, 7000)

    return {
        "EventGuid": str(uuid.uuid4()),
        "UtcTime": utc_now_iso(),
        "TelemetryCategory": "Gameplay" if "Gameplay" in event_name else "Server",
        "EventName": event_name,
        "Priority": 1 if hot else 2,
        "Fleet": {
            "Region": region
        },
        "Server": {
            "InstanceId": server_id,
            "NumPlayers": random.randint(140, 320) if hot else random.randint(30, 120)
        },
        "Match": {
            "MatchId": f"{server_id}-match"
        },
        "World": {
            "MapName": "storm_front",
            "ZoneName": zone
        },
        "Build": {
            "Changelist": "ue-cl-184920"
        },
        "Gameplay": {
            "NearbyPlayers": random.randint(120, 300) if hot else random.randint(10, 80),
            "AbilityId": random.choice(["aoe_fire_burst", "aoe_storm_pulse", "rifle_burst"])
        },
        "Host": {
            "CpuPct": random.uniform(78, 99) if hot else random.uniform(25, 70),
            "MemoryMb": random.uniform(3200, 8800)
        },
        "Frame": {
            "ServerFrameMs": frame
        },
        "Net": {
            "PacketLossPct": packet_loss,
            "OutKbps": random.uniform(2500, 12000) if hot else random.uniform(300, 2400),
            "DesyncCount": random.randint(0, 4) if hot else 0,
            "CorrectionCount": random.randint(0, 6) if hot else 0
        },
        "Replication": {
            "ReplicatedActorCount": replicated
        },
        "Physics": {
            "ActiveBodies": random.randint(60, 400) if hot else random.randint(0, 40)
        },
        "AI": {
            "ActiveAgents": random.randint(80, 320) if hot else random.randint(0, 80),
            "PathRequests": random.randint(120, 850) if hot and random.random() < 0.25 else random.randint(0, 80)
        },
        "Matchmaking": {
            "QueueLength": random.randint(0, 450) if hot and random.random() < 0.10 else 0
        },
        "Sequence": sequence_id
    }

def send_batch(collector_url: str, batch: list[dict[str, Any]]) -> None:
    url = collector_url.rstrip("/") + "/v1/events/unreal_multiplayer"
    response = requests.post(url, json=batch, timeout=10)
    if response.status_code >= 400:
        print(f"Collector returned {response.status_code}: {response.text[:1000]}")
    response.raise_for_status()

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Unreal-style multiplayer telemetry using a non-Aegis source schema.")
    parser.add_argument("--collector-url", default="http://localhost:8000")
    parser.add_argument("--events-per-second", type=int, default=500)
    parser.add_argument("--duration-sec", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=250)
    args = parser.parse_args()

    sequence_id = 0
    start = time.time()
    next_tick = start
    while time.time() - start < args.duration_sec:
        batch = []
        for _ in range(args.batch_size):
            sequence_id += 1
            batch.append(generate_unreal_event(sequence_id))
        send_batch(args.collector_url, batch)

        expected_batches_per_sec = max(args.events_per_second / args.batch_size, 1)
        next_tick += 1.0 / expected_batches_per_sec
        sleep_for = next_tick - time.time()
        if sleep_for > 0:
            time.sleep(sleep_for)

        if sequence_id % (args.batch_size * 10) == 0:
            print(f"sent_unreal_events={sequence_id}")

    print(f"complete sent_unreal_events={sequence_id}")

if __name__ == "__main__":
    main()
