import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "pulse"),
    "user":     os.getenv("DB_USER",     "pulse_user"),
    "password": os.getenv("DB_PASSWORD", "pulse_pass"),
}

EXPECTED_TABLES = [
    "users", "segments", "user_segments",
    "session_events", "tool_usage_logs", "paywall_events",
    "campaigns", "message_templates", "global_params",
    "ai_generation_log", "ab_tests", "ab_assignments",
    "ab_test_results", "notification_events", "conversion_outcomes",
]

def check_connection():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
        print("✅ Connection successful\n")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def verify_tables(conn):
    print("--- Checking tables ---")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        actual = {row[0] for row in cur.fetchall()}

    missing = set(EXPECTED_TABLES) - actual
    if not missing:
        print(f"✅ All {len(EXPECTED_TABLES)} tables found\n")
    else:
        print(f"❌ Missing tables: {missing}\n")

def verify_seed_data(conn):
    print("--- Checking seed data ---")
    checks = {
        "segments":          ("SELECT COUNT(*) FROM segments",          4),
        "campaigns":         ("SELECT COUNT(*) FROM campaigns",         4),
        "message_templates": ("SELECT COUNT(*) FROM message_templates", 4),
        "global_params":     ("SELECT COUNT(*) FROM global_params",     3),
    }
    with conn.cursor() as cur:
        for label, (query, expected) in checks.items():
            cur.execute(query)
            count = cur.fetchone()[0]
            icon = "✅" if count >= expected else "❌"
            print(f"  {icon}  {label}: {count} rows (expected {expected})")

if __name__ == "__main__":
    conn = check_connection()
    verify_tables(conn)
    print()
    verify_seed_data(conn)
    conn.close()
    print("\n✅ All checks done.")import os
import csv
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5433")),
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

def load_csv(conn, csv_path: Path, table: str) -> int:
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