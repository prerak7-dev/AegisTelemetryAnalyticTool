TOPIC_GAMEPLAY_RAW = "gameplay.events.raw"
TOPIC_SERVER_RAW = "server.metrics.raw"
TOPIC_NETWORK_RAW = "network.metrics.raw"
TOPIC_MATCHMAKING_RAW = "matchmaking.events.raw"
TOPIC_INCIDENTS = "analytics.incidents.detected"
TOPIC_VALIDATION_FAILED = "telemetry.validation.failed"

RAW_TOPICS = [
    TOPIC_GAMEPLAY_RAW,
    TOPIC_SERVER_RAW,
    TOPIC_NETWORK_RAW,
    TOPIC_MATCHMAKING_RAW,
]

PROCESSOR_TOPICS = RAW_TOPICS + [TOPIC_VALIDATION_FAILED]

def topic_for_event(event: dict) -> str:
    category = event.get("category", "gameplay")
    if category == "server":
        return TOPIC_SERVER_RAW
    if category == "network":
        return TOPIC_NETWORK_RAW
    if category == "matchmaking":
        return TOPIC_MATCHMAKING_RAW
    return TOPIC_GAMEPLAY_RAW
