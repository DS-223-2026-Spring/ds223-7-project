import os
import csv
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "pulse"),
    "user":     os.getenv("DB_USER",     "pulse_user"),
    "password": os.getenv("DB_PASSWORD", "pulse_pass"),
}

DATA_DIR = Path(__file__).parent / "data"

TABLE_MAP = {
    "users.csv":               "users",
    "session_events.csv":      "session_events",
    "tool_usage_logs.csv":     "tool_usage_logs",
    "paywall_events.csv":      "paywall_events",
    "notification_events.csv": "notification_events",
    "conversion_outcomes.csv": "conversion_outcomes",
}


def load_csv(conn, csv_path, table):
    """Load rows from a CSV file into a database table."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(f"  ⚠️  {csv_path.name} is empty, skipping")
        return 0

    cols = list(rows[0].keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)
    query = (
        f"INSERT INTO {table} ({col_names}) "
        f"VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    )

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(query, list(row.values()))
    conn.commit()
    return len(rows)


def validate_row_counts(conn):
    """Print row counts for all seeded tables."""
    print("\n--- Row Count Validation ---")
    tables = list(TABLE_MAP.values()) + [
        "segments", "campaigns", "message_templates", "global_params"
    ]
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            icon = "✅" if count > 0 else "⚠️ "
            print(f"  {icon}  {table}: {count} rows")


if __name__ == "__main__":
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
        print("✅ Connected to database\n")
    except psycopg2.OperationalError as e:
        print(f"❌ Cannot connect: {e}")
        sys.exit(1)

    print("--- Loading CSV files ---")
    for filename, table in TABLE_MAP.items():
        path = DATA_DIR / filename
        if path.exists():
            count = load_csv(conn, path, table)
            print(f"  ✅  {filename} → {table}: {count} rows loaded")
        else:
            print(f"  ⚠️   {filename} not found in data/ folder, skipping")

    validate_row_counts(conn)
    conn.close()
    print("\n✅ Done.")