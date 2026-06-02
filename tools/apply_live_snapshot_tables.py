from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import clickhouse_connect

STATEMENT_SPLIT_RE = re.compile(r";\s*(?:\n|$)")

def _load_statements(sql_path: Path) -> list[str]:
    text = sql_path.read_text(encoding="utf-8")
    statements = []
    for raw in STATEMENT_SPLIT_RE.split(text):
        statement = raw.strip()
        if not statement:
            continue
        lines = [line for line in statement.splitlines() if not line.strip().startswith("--")]
        statement = "\n".join(lines).strip()
        if statement:
            statements.append(statement)
    return statements

def main() -> None:
    parser = argparse.ArgumentParser(description="Apply AegisTelemetry live snapshot views to ClickHouse.")
    parser.add_argument("--sql", default="sql/live_snapshot_tables.sql", help="Path to the live snapshot SQL file.")
    parser.add_argument("--host", default=os.getenv("CLICKHOUSE_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CLICKHOUSE_PORT", "8123")))
    parser.add_argument("--database", default=os.getenv("CLICKHOUSE_DATABASE", "aegis_telemetry"))
    parser.add_argument("--password", default=os.getenv("CLICKHOUSE_PASSWORD", "aegis_dev_password"))
    args = parser.parse_args()

    sql_path = Path(args.sql)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    client = clickhouse_connect.get_client(
        host=args.host,
        port=args.port,
        database=args.database,
        username="default",
        password=args.password,
    )

    statements = _load_statements(sql_path)
    if not statements:
        print(f"No SQL statements found in {sql_path}")
        return

    for index, statement in enumerate(statements, start=1):
        print(f"[{index}/{len(statements)}] Applying statement...")
        client.command(statement)

    print("Live snapshot views applied successfully.")

if __name__ == "__main__":
    main()
