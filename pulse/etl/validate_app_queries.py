"""
Milestone 4 — Issue #109
Validates that all tables and views support the final app usage.
Runs every query the API and DS scripts depend on and reports results.

Run:
    # Inside Docker (etl container):
    python validate_app_queries.py

    # On host machine:
    DB_HOST=localhost DB_PORT=5433 python validate_app_queries.py
"""

import os
import sys
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

VALIDATION_QUERIES = {
    "v_platform_kpis":                "SELECT * FROM v_platform_kpis",
    "v_segment_counts":               "SELECT * FROM v_segment_counts",
    "v_segment_behavioral_averages":  "SELECT * FROM v_segment_behavioral_averages",
    "v_ab_test_summary":              "SELECT * FROM v_ab_test_summary",
    "v_segment_ab_comparison":        "SELECT * FROM v_segment_ab_comparison",
    "v_user_behavioral_features_m4":  "SELECT * FROM v_user_behavioral_features_m4 LIMIT 5",
    "v_conversion_funnel":            "SELECT * FROM v_conversion_funnel",
    "users":                          "SELECT COUNT(*) FROM users",
    "segments":                       "SELECT COUNT(*) FROM segments",
    "campaigns":                      "SELECT COUNT(*) FROM campaigns",
    "campaigns.control_message_id":   "SELECT control_message_id FROM campaigns LIMIT 1",
    "message_templates":              "SELECT COUNT(*) FROM message_templates",
    "ab_tests":                       "SELECT COUNT(*) FROM ab_tests",
    "ab_assignments":                 "SELECT COUNT(*) FROM ab_assignments",
    "ab_test_results":                "SELECT COUNT(*) FROM ab_test_results",
    "conversion_outcomes":            "SELECT COUNT(*) FROM conversion_outcomes",
    "notification_events":            "SELECT COUNT(*) FROM notification_events",
    "session_events":                 "SELECT COUNT(*) FROM session_events",
    "tool_usage_logs":                "SELECT COUNT(*) FROM tool_usage_logs",
    "paywall_events":                 "SELECT COUNT(*) FROM paywall_events",
}


def run_validations():
    """Run all validation queries and report pass/fail for each."""
    print("=" * 60)
    print("  Pulse — App Query Validation (Issue #109)")
    print("=" * 60)

    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=5)
        print("✅ Connected to database\n")
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    passed = 0
    failed = 0

    for name, query in VALIDATION_QUERIES.items():
        # Use a fresh connection for each query to avoid transaction abort
        try:
            with psycopg2.connect(**DB_CONFIG, connect_timeout=5) as c:
                with c.cursor() as cur:
                    cur.execute(query)
                    cur.fetchall()
            print(f"  ✅  {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌  {name}: {e}")
            failed += 1

    conn.close()

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_validations()