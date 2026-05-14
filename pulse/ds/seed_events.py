"""
Pulse — Event Seeder
Data Scientist: Silva Vardanyan

Seeds session_events and paywall_events with realistic timestamps so that
sessions_per_week and paywall_hits_last_7d in v_user_behavioral_features
have meaningful non-zero values.

Distribution logic per segment:
    power   — 70% of sessions in last 30 days, heavy paywall hits in last 7d
    growing — 50% of sessions in last 30 days, some paywall hits in last 7d
    casual  — 20% of sessions in last 30 days, rare paywall hits
    dormant — 0% of sessions in last 30 days, no recent paywall hits

Run:
    docker-compose exec ds python seed_events.py
"""

import os
import random
import uuid
from datetime import datetime, timedelta, timezone

import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@db:5432/pulse",
)

TOOL_NAMES       = ["thesaurus", "rhyme", "meter", "synonym", "export"]
FEATURE_BLOCKED  = ["export_limit", "advanced_export", "template_library"]

# Fraction of sessions placed within the last 30 days per segment
RECENT_SESSION_FRACTION = {
    "power":   0.70,
    "growing": 0.50,
    "casual":  0.20,
    "dormant": 0.00,
}

# Fraction of paywall hits placed within the last 7 days per segment
RECENT_PAYWALL_FRACTION = {
    "power":   0.60,
    "growing": 0.35,
    "casual":  0.10,
    "dormant": 0.00,
}


def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def random_ts(days_ago_min: float, days_ago_max: float) -> datetime:
    """Return a random UTC timestamp between days_ago_max and days_ago_min ago."""
    delta = random.uniform(days_ago_min, days_ago_max)
    return datetime.now(timezone.utc) - timedelta(days=delta)


def seed_events():
    engine = get_engine()

    with engine.connect() as conn:
        users = pd.read_sql(text("""
            SELECT u.user_id, u.total_sessions, u.total_paywall_hits,
                   u.days_since_last_login, seg.name AS segment
            FROM users u
            LEFT JOIN user_segments us ON us.user_id = u.user_id AND us.expires_at IS NULL
            LEFT JOIN segments seg      ON seg.segment_id = us.segment_id
        """), conn)

    print(f"  Seeding events for {len(users):,} users …")

    session_rows  = []
    paywall_rows  = []

    for _, u in users.iterrows():
        seg          = u["segment"] or "casual"
        n_sessions   = int(u["total_sessions"])
        n_paywall    = int(u["total_paywall_hits"])
        days_inactive = int(u["days_since_last_login"] or 999)

        recent_frac   = RECENT_SESSION_FRACTION.get(seg, 0.1)
        n_recent      = round(n_sessions * recent_frac)
        n_old         = n_sessions - n_recent

        # Build list of (started_at, is_recent) for each session
        session_times = (
            [random_ts(0, 30)   for _ in range(n_recent)] +
            [random_ts(30, 365) for _ in range(n_old)]
        )
        random.shuffle(session_times)

        # Session rows
        session_ids = []
        for started_at in session_times:
            duration  = random.randint(60, 3600)
            ended_at  = started_at + timedelta(seconds=duration)
            sid       = str(uuid.uuid4())
            session_ids.append((sid, started_at))
            session_rows.append({
                "session_id":       sid,
                "user_id":          str(u["user_id"]),
                "started_at":       started_at,
                "ended_at":         ended_at,
                "duration_seconds": duration,
                "word_count":       random.randint(50, 2000),
                "line_count":       random.randint(5, 100),
            })

        if not session_ids:
            continue

        # Paywall rows — distribute across sessions
        recent_pw_frac = RECENT_PAYWALL_FRACTION.get(seg, 0.0)
        n_recent_pw    = round(n_paywall * recent_pw_frac)
        n_old_pw       = n_paywall - n_recent_pw

        # Pick sessions in last 7 days for recent paywall hits
        recent_sessions = [(sid, ts) for sid, ts in session_ids
                           if ts >= datetime.now(timezone.utc) - timedelta(days=7)]
        old_sessions    = [(sid, ts) for sid, ts in session_ids
                           if ts < datetime.now(timezone.utc) - timedelta(days=7)]

        def make_paywall_hits(n, pool):
            rows = []
            if not pool or n == 0:
                return rows
            for _ in range(n):
                sid, session_ts = random.choice(pool)
                hit_at = session_ts + timedelta(seconds=random.randint(10, 300))
                rows.append({
                    "event_id":        str(uuid.uuid4()),
                    "user_id":         str(u["user_id"]),
                    "session_id":      sid,
                    "tool":            random.choice(TOOL_NAMES),
                    "feature_blocked": random.choice(FEATURE_BLOCKED),
                    "hit_at":          hit_at,
                })
            return rows

        paywall_rows.extend(make_paywall_hits(n_recent_pw, recent_sessions or session_ids))
        paywall_rows.extend(make_paywall_hits(n_old_pw,    old_sessions    or session_ids))

    # Write to DB
    print(f"  Inserting {len(session_rows):,} session_events …")
    print(f"  Inserting {len(paywall_rows):,} paywall_events …")

    with engine.begin() as conn:
        # Clear existing (safe — counters on users table are authoritative)
        conn.execute(text("DELETE FROM paywall_events"))
        conn.execute(text("DELETE FROM session_events"))

        for row in session_rows:
            conn.execute(text("""
                INSERT INTO session_events
                    (session_id, user_id, started_at, ended_at, duration_seconds, word_count, line_count)
                VALUES
                    (:session_id, :user_id, :started_at, :ended_at, :duration_seconds, :word_count, :line_count)
            """), row)

        for row in paywall_rows:
            conn.execute(text("""
                INSERT INTO paywall_events
                    (event_id, user_id, session_id, tool, feature_blocked, hit_at)
                VALUES
                    (:event_id, :user_id, :session_id, CAST(:tool AS tool_name), :feature_blocked, :hit_at)
            """), row)

    print("  Done.")


if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — Event Seeder")
    print("=" * 65)
    seed_events()

    # Show result
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM v_segment_behavioral_averages")).mappings().all()
    print("\n  Behavioral averages after seeding:")
    print(f"  {'Segment':<10} {'Sessions/wk':>12} {'Exports':>10} {'Paywall/wk':>12}")
    print("  " + "-" * 46)
    for r in result:
        print(f"  {r['segment_name']:<10} {str(r['avg_sessions_per_week']):>12} "
              f"{str(r['avg_exports_per_week']):>10} {str(r['avg_paywall_hits']):>12}")
    print("=" * 65)
