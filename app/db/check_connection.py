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
    print("\n✅ All checks done.")