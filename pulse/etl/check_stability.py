"""
Milestone 4 — Issue #110
Checks that data loading and retrieval remain stable after integration.
Tests insert, select, update, delete and verifies row counts are consistent.

Run:
    python check_stability.py
"""

import os
import sys
import uuid
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "db"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "pulse"),
    "user":     os.getenv("DB_USER",     "pulse_user"),
    "password": os.getenv("DB_PASSWORD", "pulse_pass"),
}

TEST_USER_ID = str(uuid.uuid4())


def get_conn():
    """Return a new database connection."""
    return psycopg2.connect(**DB_CONFIG, connect_timeout=5)


def test_connection():
    """Test that database connection is stable."""
    try:
        conn = get_conn()
        conn.close()
        print("  ✅  Connection stable")
        return True
    except Exception as e:
        print(f"  ❌  Connection failed: {e}")
        return False


def test_insert(conn):
    """Test inserting a row into users table."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, email, display_name, plan, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (TEST_USER_ID, f"test_{TEST_USER_ID[:8]}@test.com",
                  "Test User", "free", "active"))
        conn.commit()
        print("  ✅  INSERT stable")
        return True
    except Exception as e:
        print(f"  ❌  INSERT failed: {e}")
        return False


def test_select(conn):
    """Test selecting the inserted row."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (TEST_USER_ID,))
            row = cur.fetchone()
            assert row is not None, "Row not found after insert"
        print("  ✅  SELECT stable")
        return True
    except Exception as e:
        print(f"  ❌  SELECT failed: {e}")
        return False


def test_update(conn):
    """Test updating the inserted row."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users SET status = 'inactive'
                WHERE user_id = %s
            """, (TEST_USER_ID,))
        conn.commit()
        print("  ✅  UPDATE stable")
        return True
    except Exception as e:
        print(f"  ❌  UPDATE failed: {e}")
        return False


def test_delete(conn):
    """Test deleting the inserted row."""
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE user_id = %s", (TEST_USER_ID,))
        conn.commit()
        print("  ✅  DELETE stable")
        return True
    except Exception as e:
        print(f"  ❌  DELETE failed: {e}")
        return False


def test_row_counts(conn):
    """Verify seed tables have expected minimum row counts."""
    checks = {
        "segments":          4,
        "campaigns":         4,
        "message_templates": 4,
        "global_params":     3,
    }
    all_passed = True
    with conn.cursor() as cur:
        for table, expected in checks.items():
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            if count >= expected:
                print(f"  ✅  {table}: {count} rows (expected ≥ {expected})")
            else:
                print(f"  ❌  {table}: {count} rows (expected ≥ {expected})")
                all_passed = False
    return all_passed


def test_views_return_data(conn):
    """Check that all key views execute without error."""
    views = [
        "v_platform_kpis",
        "v_segment_counts",
        "v_segment_behavioral_averages",
        "v_ab_test_summary",
        "v_segment_ab_comparison",
        "v_conversion_funnel",
    ]
    all_passed = True
    with conn.cursor() as cur:
        for view in views:
            try:
                cur.execute(f"SELECT * FROM {view}")
                cur.fetchall()
                print(f"  ✅  {view} executes cleanly")
            except Exception as e:
                print(f"  ❌  {view} failed: {e}")
                all_passed = False
    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("  Pulse — Data Stability Check (Issue #110)")
    print("=" * 60)

    if not test_connection():
        sys.exit(1)

    conn = get_conn()
    results = []

    print("\n--- CRUD Operations ---")
    results.append(test_insert(conn))
    results.append(test_select(conn))
    results.append(test_update(conn))
    results.append(test_delete(conn))

    print("\n--- Row Count Checks ---")
    results.append(test_row_counts(conn))

    print("\n--- View Stability ---")
    results.append(test_views_return_data(conn))

    conn.close()

    passed = sum(results)
    failed = len(results) - passed

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ All stability checks passed.")