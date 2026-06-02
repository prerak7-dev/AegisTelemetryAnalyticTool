from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from services.dashboard.performance_config import demo_control_cfg

PROCESS_STATE_KEY = "aegis_demo_scenario_processes"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def scenario_library_path() -> Path:
    return Path(str(demo_control_cfg("scenario_library_path", "/app/config/demo_scenarios.json")))

def scenario_history_path() -> Path:
    return Path(str(demo_control_cfg("scenario_history_path", "/app/data/demo_scenario_history.json")))

def load_scenario_library() -> dict[str, Any]:
    path = scenario_library_path()
    fallback = {"version": "0", "scenarios": []}

    candidate_paths = [
        path,
        Path("config/demo_scenarios.json"),
        Path.cwd() / "config" / "demo_scenarios.json",
        Path(__file__).resolve().parents[2] / "config" / "demo_scenarios.json",
    ]

    selected_path = None
    for candidate in candidate_paths:
        if candidate.exists():
            selected_path = candidate
            break

    if selected_path is None:
        return fallback

    try:
        payload = json.loads(selected_path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

    if not isinstance(payload, dict):
        return fallback
    payload.setdefault("scenarios", [])
    return payload

def save_history_record(record: dict[str, Any]) -> None:
    path = scenario_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {"records": []}
    else:
        payload = {"records": []}

    payload.setdefault("records", []).append(record)
    payload["updated_at"] = utc_now_iso()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

def load_history_records(limit: int = 100) -> list[dict[str, Any]]:
    path = scenario_history_path()
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    records = list(payload.get("records", []))
    return records[-limit:]

def process_state() -> dict[str, subprocess.Popen]:
    return st.session_state.setdefault(PROCESS_STATE_KEY, {})

def active_process_records() -> list[dict[str, Any]]:
    records = []
    now = datetime.now(timezone.utc)
    for key, process in list(process_state().items()):
        status = "running" if process.poll() is None else f"exited:{process.returncode}"

        scenario_id = ""
        command_label = ""
        started_at = ""
        elapsed_seconds = 0
        try:
            scenario_id, command_label, started_at = key.split(":", 2)
            started_dt = datetime.fromisoformat(started_at)
            if started_dt.tzinfo is None:
                started_dt = started_dt.replace(tzinfo=timezone.utc)
            elapsed_seconds = int((now - started_dt.astimezone(timezone.utc)).total_seconds())
        except Exception:
            pass

        records.append({
            "process_key": key,
            "scenario_id": scenario_id,
            "command_label": command_label,
            "started_at": started_at,
            "elapsed_seconds": max(0, elapsed_seconds),
            "pid": process.pid,
            "status": status,
        })
    return records

def cleanup_finished_processes() -> None:
    for key, process in list(process_state().items()):
        if process.poll() is not None:
            del process_state()[key]

def stop_process(process_key: str) -> bool:
    process = process_state().get(process_key)
    if not process:
        return False

    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except Exception:
            process.kill()

    del process_state()[process_key]
    return True

def stop_all_processes() -> int:
    keys = list(process_state().keys())
    stopped = 0
    for key in keys:
        if stop_process(key):
            stopped += 1
    return stopped

def build_command(command_args: list[str], *, duration_sec: int, events_per_second: int) -> list[str]:
    """Build the command executed inside the dashboard container."""
    python_executable = str(demo_control_cfg("python_executable", "python"))
    script_path = str(demo_control_cfg("simulator_script_path", "/app/simulator/generate_traffic.py"))
    collector_url = str(demo_control_cfg("collector_url", "http://collector:8000"))
    batch_size = int(demo_control_cfg("default_batch_size", 250) or 250)

    return [
        python_executable,
        script_path,
        "--collector-url",
        collector_url,
        "--events-per-second",
        str(int(events_per_second)),
        "--duration-sec",
        str(int(duration_sec)),
        "--batch-size",
        str(batch_size),
        *[str(arg) for arg in command_args],
    ]

def build_host_command(command_args: list[str], *, duration_sec: int, events_per_second: int) -> list[str]:
    """Build a command developers can copy/run from the project root on the host."""
    python_executable = str(demo_control_cfg("host_python_executable", "python"))
    script_path = str(demo_control_cfg("host_simulator_script_path", "simulator/generate_traffic.py"))
    collector_url = str(demo_control_cfg("host_collector_url", "http://localhost:8000"))
    batch_size = int(demo_control_cfg("default_batch_size", 250) or 250)

    return [
        python_executable,
        script_path,
        "--collector-url",
        collector_url,
        "--events-per-second",
        str(int(events_per_second)),
        "--duration-sec",
        str(int(duration_sec)),
        "--batch-size",
        str(batch_size),
        *[str(arg) for arg in command_args],
    ]

def shell_command(command: list[str]) -> str:
    def quote(part: str) -> str:
        if not part:
            return "''"
        if any(ch.isspace() for ch in part) or any(ch in part for ch in ['"', "'", "\\"]):
            return "'" + part.replace("'", "'\"'\"'") + "'"
        return part
    return " ".join(quote(str(part)) for part in command)

def can_launch_processes() -> bool:
    return bool(demo_control_cfg("allow_subprocess_launch", True))

def launch_command(
    *,
    scenario_id: str,
    command_label: str,
    command: list[str],
) -> tuple[bool, str]:
    if not can_launch_processes():
        return False, "Subprocess launch is disabled by configuration."

    max_processes = int(demo_control_cfg("max_parallel_scenario_processes", 4) or 4)
    cleanup_finished_processes()

    if len(process_state()) >= max_processes:
        return False, f"Maximum active demo processes reached: {max_processes}"

    process_key = f"{scenario_id}:{command_label}:{utc_now_iso()}"
    try:
        env = os.environ.copy()
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
    except Exception as exc:
        return False, str(exc)

    process_state()[process_key] = process
    save_history_record({
        "event": "launch",
        "scenario_id": scenario_id,
        "command_label": command_label,
        "command": shell_command(command),
        "pid": process.pid,
        "created_at": utc_now_iso(),
    })
    return True, process_key
