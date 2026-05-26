# Telemetry Taxonomy

## Design goals

The taxonomy separates player behavior, gameplay systems, server health, network quality, and matchmaking pressure so performance incidents can be attributed to gameplay context.

## Priority 0 — never drop

- `server_hitch_detected`
- `server_frame_sample`
- `desync_detected`
- `rubberband_detected`
- `disconnect`
- `match_crash`
- `match_result`

## Priority 1 — aggregate if needed

- `ability_cast`
- `aoe_ability_cast`
- `projectile_spawned`
- `physics_event`
- `object_replicated`
- `damage_resolved`
- `ai_pathfinding_request`

## Priority 2 — sample under load

- `player_position_sample`
- `zone_entered`
- `camera_state`
- `inventory_updated`

## Priority 3 — drop first

- `debug_trace`
- `cosmetic_event`
- `minor_ui_event`
