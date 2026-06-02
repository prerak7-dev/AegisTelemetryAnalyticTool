from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from services.dashboard.performance_config import incident_workflow_cfg

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def workflow_store_path() -> Path:
    configured = str(incident_workflow_cfg("store_path", "/app/data/incident_workflow.json"))
    return Path(configured)

def _empty_payload() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_at": utc_now_iso(),
        "records": {},
        "notes": {},
    }

def load_workflow_store() -> dict[str, Any]:
    path = workflow_store_path()
    if not path.exists():
        return _empty_payload()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _empty_payload()

    if not isinstance(payload, dict):
        return _empty_payload()

    payload.setdefault("version", 1)
    payload.setdefault("updated_at", utc_now_iso())
    payload.setdefault("records", {})
    payload.setdefault("notes", {})
    return payload

def save_workflow_store(payload: dict[str, Any]) -> None:
    path = workflow_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = utc_now_iso()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

def default_record(incident_id: str) -> dict[str, Any]:
    return {
        "incident_id": incident_id,
        "status": str(incident_workflow_cfg("default_status", "open")),
        "assigned_owner": "Unassigned",
        "next_action": str(incident_workflow_cfg("escalation.default_next_action", "Review incident.")),
        "resolution_summary": "",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }

def get_record(incident_id: str) -> dict[str, Any]:
    payload = load_workflow_store()
    records = payload.setdefault("records", {})
    if incident_id not in records:
        records[incident_id] = default_record(incident_id)
    return dict(records[incident_id])

def upsert_record(
    incident_id: str,
    *,
    status: str,
    assigned_owner: str,
    next_action: str,
    resolution_summary: str,
) -> dict[str, Any]:
    payload = load_workflow_store()
    records = payload.setdefault("records", {})
    existing = records.get(incident_id, default_record(incident_id))
    existing.update({
        "incident_id": incident_id,
        "status": status,
        "assigned_owner": assigned_owner,
        "next_action": next_action,
        "resolution_summary": resolution_summary,
        "updated_at": utc_now_iso(),
    })
    records[incident_id] = existing
    save_workflow_store(payload)
    return dict(existing)

def add_note(incident_id: str, note: str, author: str = "Analyst") -> dict[str, Any] | None:
    note = (note or "").strip()
    if not note:
        return None

    payload = load_workflow_store()
    notes = payload.setdefault("notes", {})
    note_record = {
        "incident_id": incident_id,
        "author": author or "Analyst",
        "note": note,
        "created_at": utc_now_iso(),
    }
    notes.setdefault(incident_id, []).append(note_record)
    save_workflow_store(payload)
    return note_record

def get_notes(incident_id: str) -> list[dict[str, Any]]:
    payload = load_workflow_store()
    notes = payload.setdefault("notes", {})
    return list(notes.get(incident_id, []))

def records_dataframe_rows() -> list[dict[str, Any]]:
    payload = load_workflow_store()
    return list(payload.get("records", {}).values())

def merge_workflow_rows(incident_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = load_workflow_store()
    records = payload.setdefault("records", {})
    merged = []

    for incident in incident_rows:
        incident_id = str(incident.get("incident_id", ""))
        workflow = records.get(incident_id, default_record(incident_id))
        merged.append({**incident, **{
            "workflow_status": workflow.get("status", "open"),
            "assigned_owner": workflow.get("assigned_owner", "Unassigned"),
            "next_action": workflow.get("next_action", ""),
            "resolution_summary": workflow.get("resolution_summary", ""),
            "workflow_updated_at": workflow.get("updated_at", ""),
        }})

    return merged
