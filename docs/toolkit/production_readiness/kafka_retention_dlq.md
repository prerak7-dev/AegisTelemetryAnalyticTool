# Kafka Retention and Dead-Letter Strategy

AegisTelemetry uses Redpanda/Kafka-compatible topics.

## Topic categories

| Category | Example |
|---|---|
| Raw gameplay telemetry | `telemetry.gameplay` |
| Validation failures / DLQ | `telemetry.validation_failed` |
| Incidents | `telemetry.incidents` |

## Dead-letter topic

The validation failure topic acts as the current dead-letter path:

```text
telemetry.validation_failed
```

Events are written there when:

- mapping fails
- schema validation fails
- malformed events cannot be normalized

## DLQ payload should include

```text
failed_at
source_profile
event
raw_event
error
```

## Retention recommendation

For local/demo:

```text
raw telemetry: 24h
incidents: 7d
validation failures: 7d
```

For production:

```text
raw telemetry: 24h to 72h
aggregated telemetry: 30d+
incidents: 90d+
validation failures: 14d+
```

## Example Redpanda topic commands

```bash
rpk topic create telemetry.gameplay --brokers localhost:19092
rpk topic create telemetry.validation_failed --brokers localhost:19092
rpk topic create telemetry.incidents --brokers localhost:19092
```

Set retention:

```bash
rpk topic alter-config telemetry.gameplay --set retention.ms=86400000 --brokers localhost:19092
rpk topic alter-config telemetry.validation_failed --set retention.ms=604800000 --brokers localhost:19092
```

## Consumer lag monitoring

Track:

- consumer group ID
- topic
- partition
- current offset
- high-watermark offset
- lag

The processor group defaults to:

```text
aegis-processor-local
```

## Poison-message strategy

For production:

```text
1. Validate before processing
2. Write bad events to DLQ
3. Keep original raw payload
4. Include error reason
5. Add replay tooling
6. Add DLQ review dashboard
```
