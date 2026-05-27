from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_common.canonical import CANONICAL_DEFAULTS, CANONICAL_FIELDS, CANONICAL_NUMERIC_FIELDS

class MappingError(ValueError):
    pass

@dataclass(frozen=True)
class MappingProfile:
    profile_name: str
    description: str
    version: str
    passthrough: bool
    field_map: dict[str, list[str]]
    defaults: dict[str, Any]
    event_type_map: dict[str, str]
    value_maps: dict[str, dict[str, Any]]
    source_path: str

    @classmethod
    def from_json_file(cls, path: Path) -> "MappingProfile":
        payload = json.loads(path.read_text(encoding="utf-8"))
        field_map = {
            key: value if isinstance(value, list) else [value]
            for key, value in payload.get("field_map", {}).items()
        }
        return cls(
            profile_name=payload.get("profile_name") or path.stem,
            description=payload.get("description", ""),
            version=payload.get("version", "1.0.0"),
            passthrough=bool(payload.get("passthrough", False)),
            field_map=field_map,
            defaults=payload.get("defaults", {}),
            event_type_map=payload.get("event_type_map", {}),
            value_maps=payload.get("value_maps", {}),
            source_path=str(path),
        )

def load_profiles(profile_dir: Path) -> dict[str, MappingProfile]:
    profiles: dict[str, MappingProfile] = {}
    if not profile_dir.exists():
        return profiles

    for path in sorted(profile_dir.glob("*.json")):
        profile = MappingProfile.from_json_file(path)
        profiles[profile.profile_name] = profile

    return profiles

def get_path(payload: dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current

def first_present(payload: dict[str, Any], paths: list[str]) -> Any:
    for path in paths:
        value = get_path(payload, path)
        if value is not None:
            return value
    return None

def coerce_numeric(field: str, value: Any) -> Any:
    if field not in CANONICAL_NUMERIC_FIELDS or value in (None, ""):
        return value

    caster = CANONICAL_NUMERIC_FIELDS[field]
    try:
        return caster(value)
    except (TypeError, ValueError) as exc:
        raise MappingError(f"Could not coerce field '{field}' value '{value}' to {caster.__name__}") from exc

def normalize_with_profile(raw_event: dict[str, Any], profile: MappingProfile) -> dict[str, Any]:
    if profile.passthrough:
        canonical = copy.deepcopy(raw_event)
    else:
        canonical = {}

    defaults = {**CANONICAL_DEFAULTS, **profile.defaults}
    for key, value in defaults.items():
        canonical.setdefault(key, value)

    for canonical_field, source_paths in profile.field_map.items():
        value = first_present(raw_event, source_paths)
        if value is not None:
            canonical[canonical_field] = value

    # Keep original profile and raw event for traceability/debugging.
    canonical["source_profile"] = profile.profile_name
    canonical["source_event_raw"] = raw_event

    if canonical.get("event_type") in profile.event_type_map:
        canonical["event_type"] = profile.event_type_map[canonical["event_type"]]

    for field, mapping in profile.value_maps.items():
        value = canonical.get(field)
        if value in mapping:
            canonical[field] = mapping[value]

    # If non-passthrough, intentionally only mapped canonical fields plus traceability are emitted.
    if not profile.passthrough:
        canonical = {
            key: value for key, value in canonical.items()
            if key in CANONICAL_FIELDS or key in {"source_profile", "source_event_raw"}
        }

    for field in list(canonical.keys()):
        canonical[field] = coerce_numeric(field, canonical[field])

    return canonical

def profile_summaries(profiles: dict[str, MappingProfile]) -> list[dict[str, Any]]:
    return [
        {
            "profile_name": profile.profile_name,
            "version": profile.version,
            "description": profile.description,
            "passthrough": profile.passthrough,
            "mapped_fields": sorted(profile.field_map.keys()),
        }
        for profile in sorted(profiles.values(), key=lambda item: item.profile_name)
    ]
