"""ETL entry point — verifies DB connection/tables then loads CSV seed data."""
import sys
import psycopg2
from pathlib import Path
import csv
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "db"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "pulse"),
    "user":     os.getenv("DB_USER",     "pulse_user"),
    "password": os.getenv("DB_PASSWORD", "pulse_pass"),
}

DATA_DIR = Path(__file__).parent / "data"

# CSV files → target tables (supplemental rows only; schema SQL seeds core data)
TABLE_MAP = {
    "users.csv":               "users",
    "session_events.csv":      "session_events",
    "tool_usage_logs.csv":     "tool_usage_logs",
    "paywall_events.csv":      "paywall_events",
    "notification_events.csv": "notification_events",
    "conversion_outcomes.csv": "conversion_outcomes",
}


def load_csv(conn, csv_path, table):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return 0
    cols = rows[0].keys()
    col_names = ", ".join(cols)
    placeholders = ", ".join([f"%({c})s" for c in cols])
    loaded = 0
    with conn.cursor() as cur:
        for row in rows:
            try:
                cur.execute(
                    f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                    row,
                )
                loaded += 1
            except Exception:
                conn.rollback()
    conn.commit()
    return loaded


if __name__ == "__main__":
    print("=" * 50)
    print("Pulse ETL — starting")
    print("=" * 50)

    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
        print("✅ Connected to database")
    except psycopg2.OperationalError as e:
        print(f"❌ Cannot connect: {e}")
        sys.exit(1)

    # Check if schema already seeded users (via 01_schema.sql PL/pgSQL block)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]

    print(f"\n  Users in DB: {user_count}")
    if user_count >= 442:
        print("  ✅ Schema seed already ran — 442 users present.")
    else:
        print("  ⚠️  Fewer than 442 users — loading supplemental CSV data.")
        for filename, table in TABLE_MAP.items():
            path = DATA_DIR / filename
            if path.exists():
                count = load_csv(conn, path, table)
                print(f"  ✅  {filename} → {table}: {count} rows loaded")
            else:
                print(f"  ⚠️   {filename} not found, skipping")

    conn.close()
    print("\n" + "=" * 50)
    print("Pulse ETL — complete")
    print("=" * 50)
