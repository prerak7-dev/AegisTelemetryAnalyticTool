from __future__ import annotations

import argparse
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import requests

REGIONS = ["NA-East", "NA-West", "EU-West", "EU-Central", "South America", "Middle East", "Southeast Asia", "Japan", "Australia"]
MAPS = ["storm_front", "ancient_arena", "zero_point_city", "icebound_pass"]
ZONES = ["northern_ridge", "market_square", "central_lane", "river_delta", "crater_field", "skybridge", "forest_outpost"]
ABILITIES = ["rifle_burst", "dash", "grenade", "aoe_fire_burst", "aoe_storm_pulse", "healing_field", "sniper_shot"]

MELTDOWN_SERVERS = {
    "EU-West": ["eu-west-incident-001", "eu-west-incident-002", "eu-west-incident-003"],
    "NA-East": ["na-east-incident-001", "na-east-incident-002"],
}

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

def base_event(
    scenario: str,
    sequence_id: int,
    category: str,
    event_type: str,
    region: str,
    server_id: str,
    match_id: str,
    map_id: str,
    zone_id: str,
    priority: int = 1,
) -> dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "event_time": utc_now_iso(),
        "category": category,
        "event_type": event_type,
        "priority": priority,
        "region": region,
        "server_id": server_id,
        "match_id": match_id,
        "map_id": map_id,
        "zone_id": zone_id,
        "build_version": "0.2.0-phase2",
        "sequence_id": sequence_id,
        "server_tick": sequence_id * 2,
        "scenario": scenario,
    }

def choose_topology(scenario: str) -> tuple[str, str, str, str, str]:
    region = random.choices(REGIONS, weights=[1.3, 1.0, 1.6, 1.2, 0.7, 0.5, 0.8, 0.7, 0.5], k=1)[0]
    map_id = random.choice(MAPS)
    zone_id = random.choice(ZONES)
    server_id = f"{region.lower().replace(' ', '-').replace('_', '-')}-{random.randint(1, 80):03d}"
    match_id = f"match_{random.randint(10000, 99999)}"

    # Stable topology for incident scenarios so aggregates accumulate in the same server/zone windows.
    if scenario == "weekend_event_meltdown" and random.random() < 0.72:
        region = random.choice(["EU-West", "NA-East"])
        map_id = "storm_front"
        zone_id = "northern_ridge"
        server_id = random.choice(MELTDOWN_SERVERS[region])
        match_id = f"{server_id}-live-event"

    return region, server_id, match_id, map_id, zone_id

def generate_event(scenario: str, sequence_id: int, invalid_rate: float = 0.0) -> dict[str, Any]:
    region, server_id, match_id, map_id, zone_id = choose_topology(scenario)

    nearby = int(clamp(random.gauss(24, 12), 1, 80))
    player_count = int(clamp(random.gauss(72, 30), 8, 180))
    cpu = clamp(random.gauss(48, 10), 15, 92)
    frame_ms = clamp(random.gauss(26, 6), 8, 70)
    packet_loss = clamp(random.gauss(0.8, 0.5), 0, 8)
    packet_out = clamp(random.gauss(750, 240), 100, 2500)
    replicated_objects = int(clamp(random.gauss(3000, 1100), 100, 9000))
    physics_events = int(clamp(random.gauss(8, 5), 0, 40))
    ai_agents_active = int(clamp(random.gauss(25, 18), 0, 120))
    ai_pathfinding_requests = int(clamp(random.gauss(12, 8), 0, 60))
    matchmaking_queue_length = 0
    event_type = random.choices(
        ["player_position_sample", "ability_cast", "server_frame_sample", "object_replicated", "physics_event"],
        weights=[4, 3, 2, 1, 1],
        k=1,
    )[0]
    category = "gameplay"
    priority = 2
    ability_id = random.choice(ABILITIES)

    if scenario == "weekend_event_meltdown":
        if region in {"EU-West", "NA-East"} and zone_id == "northern_ridge":
            player_count += random.randint(80, 180)
            nearby += random.randint(70, 160)
            cpu += random.uniform(18, 38)
            frame_ms += random.uniform(18, 58)
            packet_loss += random.uniform(0.8, 5.0)
            replicated_objects += random.randint(7000, 18000)

        if random.random() < 0.68:
            ability_id = random.choice(["aoe_fire_burst", "aoe_storm_pulse"])
            event_type = "aoe_ability_cast"
            priority = 1
            physics_events += random.randint(35, 150)
            frame_ms += random.uniform(10, 35)

    elif scenario == "physics_spike":
        if random.random() < 0.45:
            event_type = "physics_event"
            priority = 1
            physics_events += random.randint(60, 220)
            cpu += random.uniform(20, 35)
            frame_ms += random.uniform(20, 50)

    elif scenario == "replication_overload":
        if random.random() < 0.50:
            event_type = "object_replicated"
            priority = 1
            replicated_objects += random.randint(9000, 22000)
            packet_out += random.uniform(2500, 6500)
            packet_loss += random.uniform(2, 7)
            frame_ms += random.uniform(6, 20)

    elif scenario == "ai_pathfinding_spike":
        if random.random() < 0.55:
            event_type = "ai_pathfinding_request"
            priority = 1
            ai_agents_active += random.randint(140, 320)
            ai_pathfinding_requests += random.randint(250, 900)
            cpu += random.uniform(18, 38)
            frame_ms += random.uniform(18, 55)

    elif scenario == "memory_pressure":
        if random.random() < 0.55:
            event_type = random.choice(["object_replicated", "physics_event", "ability_cast"])
            priority = 1
            replicated_objects += random.randint(6000, 16000)
            physics_events += random.randint(20, 130)
            cpu += random.uniform(8, 22)
            frame_ms += random.uniform(10, 45)

    elif scenario == "network_packet_pressure":
        if random.random() < 0.60:
            event_type = "object_replicated"
            priority = 1
            replicated_objects += random.randint(12000, 26000)
            packet_out += random.uniform(5500, 11000)
            packet_loss += random.uniform(4, 12)
            frame_ms += random.uniform(8, 28)

    elif scenario == "region_login_surge":
        if region == "EU-West":
            category = "matchmaking"
            event_type = "session_started"
            priority = 1
            player_count += random.randint(100, 240)
            cpu += random.uniform(12, 25)
            packet_out += random.uniform(1200, 2800)
            matchmaking_queue_length += random.randint(80, 600)

    event = base_event(scenario, sequence_id, category, event_type, region, server_id, match_id, map_id, zone_id, priority)

    desync = 0
    rubberband = 0
    if frame_ms > 50:
        rubberband = random.randint(0, 4)
    if frame_ms > 65 or packet_loss > 5:
        desync = random.randint(0, 3)

    event.update({
        "player_count": int(clamp(player_count, 0, 500)),
        "players_nearby": int(clamp(nearby, 0, 320)),
        "ability_id": ability_id,
        "cpu_percent": round(clamp(cpu, 0, 100), 2),
        "memory_mb": round(clamp(random.gauss(7600, 1400), 1800, 12000), 2) if scenario == "memory_pressure" else round(clamp(random.gauss(4200, 700), 1800, 9000), 2),
        "server_frame_ms": round(clamp(frame_ms, 4, 160), 2),
        "packet_loss_percent": round(clamp(packet_loss, 0, 20), 2),
        "packet_out_kbps": round(clamp(packet_out, 10, 12000), 2),
        "desync_count": desync,
        "rubberband_count": rubberband,
        "replicated_objects": int(clamp(replicated_objects, 0, 35000)),
        "physics_events": int(clamp(physics_events, 0, 500)),
        "ai_agents_active": int(clamp(ai_agents_active, 0, 600)),
        "ai_pathfinding_requests": int(clamp(ai_pathfinding_requests, 0, 1200)),
        "matchmaking_queue_length": int(clamp(matchmaking_queue_length, 0, 1000)),
    })

    # Optional data-quality demo: inject schema-invalid events.
    if invalid_rate > 0 and random.random() < invalid_rate:
        if random.random() < 0.5:
            event["cpu_percent"] = 140.0
        else:
            event.pop("server_id", None)

    return event

def send_batch(collector_url: str, batch: list[dict[str, Any]]) -> None:
    url = collector_url.rstrip("/") + "/v1/events"
    response = requests.post(url, json=batch, timeout=10)
    if response.status_code >= 400:
        print(f"Collector returned {response.status_code}: {response.text[:1000]}")
    response.raise_for_status()

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic gameplay telemetry.")
    parser.add_argument("--scenario", default="normal_load", choices=[
        "normal_load",
        "weekend_event_meltdown",
        "physics_spike",
        "region_login_surge",
        "replication_overload",
        "ai_pathfinding_spike",
        "memory_pressure",
        "network_packet_pressure",
    ])
    parser.add_argument("--collector-url", default="http://localhost:8000")
    parser.add_argument("--events-per-second", type=int, default=250)
    parser.add_argument("--duration-sec", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument("--invalid-rate", type=float, default=0.0, help="Optional validation-failure injection rate from 0.0 to 1.0")
    args = parser.parse_args()

    sequence_id = 0
    start = time.time()
    next_tick = start
    print(f"Generating scenario={args.scenario}, eps={args.events_per_second}, duration={args.duration_sec}s")

    while time.time() - start < args.duration_sec:
        batch = []
        for _ in range(args.batch_size):
            sequence_id += 1
            batch.append(generate_event(args.scenario, sequence_id, invalid_rate=args.invalid_rate))

        send_batch(args.collector_url, batch)
        expected_batches_per_sec = max(args.events_per_second / args.batch_size, 1)
        next_tick += 1.0 / expected_batches_per_sec
        sleep_for = next_tick - time.time()
        if sleep_for > 0:
            time.sleep(sleep_for)

        if sequence_id % (args.batch_size * 10) == 0:
            print(f"sent_events={sequence_id}")

    print(f"complete sent_events={sequence_id}")

if __name__ == "__main__":
    main()
