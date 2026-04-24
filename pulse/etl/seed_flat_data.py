"""Seed synthetic behavioral data into the Pulse database.

Generates realistic users + behavioral events for all four segments.
Triggers in the DB handle aggregated columns (total_sessions, etc.)
so this script inserts raw events and lets the DB stay consistent.
"""
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

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

random.seed(42)

# Armenian names for realistic test data
FIRST_NAMES = [
    "Ani", "Nare", "Lilit", "Arpi", "Marine", "Gohar", "Sona", "Lusine",
    "Anahit", "Nvard", "Mane", "Kristine", "Tamara", "Astghik", "Zaruhi",
    "Vardan", "Armen", "Tigran", "Narek", "Davit", "Artur", "Hayk", "Aram",
    "Sargis", "Karen", "Albert", "Areg", "Levon", "Hakob", "Ruben", "Ashot",
]
LAST_NAMES = [
    "Petrosyan", "Hakobyan", "Grigoryan", "Sargsyan", "Hovhannisyan",
    "Gevorgyan", "Avagyan", "Mkrtchyan", "Harutyunyan", "Abrahamyan",
    "Simonyan", "Vardanyan", "Galstyan", "Karapetyan", "Danielyan",
    "Ghazaryan", "Asatryan", "Mirzoyan", "Poghosyan", "Zakaryan",
]

# Segment behavioral profiles — counts roughly match README proportions
# (scaled to ~10% to keep seeding fast)
PROFILES = {
    "power":   {
        "count": 124,
        "sessions":   (15, 35),
        "exports":    (8,  20),
        "paywall":    (8,  20),
        "thesaurus":  (15, 40),
        "days_ago":   (0,  3),     # last active very recently
    },
    "growing": {
        "count": 158,
        "sessions":   (6,  14),
        "exports":    (2,  8),
        "paywall":    (2,  8),
        "thesaurus":  (5,  15),
        "days_ago":   (3,  10),
    },
    "casual":  {
        "count": 98,
        "sessions":   (2,  5),
        "exports":    (0,  2),
        "paywall":    (0,  2),
        "thesaurus":  (1,  5),
        "days_ago":   (10, 30),
    },
    "dormant": {
        "count": 62,
        "sessions":   (1,  2),
        "exports":    (0,  1),
        "paywall":    (0,  1),
        "thesaurus":  (0,  2),
        "days_ago":   (30, 90),
    },
}

TOOLS = ["thesaurus", "rhyme", "meter", "synonym", "export"]
NOTIF_EVENTS = ["shown", "opened", "clicked", "dismissed"]
CHANNELS = ["in_app_popup", "push_notification", "email"]

CONVERSION_RATE = 0.054   # 5.4% — matches README KPIs
CHURN_30D_RATE  = 0.17    # 17% churn → 83% 30-day retention


def new_id():
    return str(uuid.uuid4())


def rand_ts(days_min, days_max):
    """Random UTC timestamp between days_min and days_max days ago."""
    now = datetime.now(timezone.utc)
    days = random.uniform(days_min, days_max)
    mins = random.uniform(0, 59)
    hrs  = random.uniform(7, 23)     # working hours only
    return now - timedelta(days=days, hours=hrs, minutes=mins)


def rand_name(index):
    first = random.choice(FIRST_NAMES)
    last  = random.choice(LAST_NAMES)
    email = f"{first.lower()}.{last.lower()}.{index}@armat.am"
    return f"{first} {last}", email


def main():
    print("🌱 Seeding synthetic behavioral data...")

    conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Idempotency guard ───────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] > 0:
        print("✅ Users already seeded — skipping.")
        cur.close()
        conn.close()
        return

    # ── Load reference data (seeded by SQL init script) ─────────────────────────
    cur.execute("SELECT name, segment_id FROM segments")
    seg_ids = dict(cur.fetchall())

    cur.execute("""
        SELECT s.name, c.campaign_id, c.active_message_id, c.channel
        FROM   campaigns c
        JOIN   segments  s ON s.segment_id = c.segment_id
        WHERE  c.active_message_id IS NOT NULL
    """)
    camp_info = {row[0]: (row[1], row[2], row[3]) for row in cur.fetchall()}

    global_counter = 0
    total_inserted = 0

    for seg_name, profile in PROFILES.items():
        seg_id = seg_ids.get(seg_name)
        if not seg_id:
            print(f"  ⚠️  Segment '{seg_name}' not found in DB — skipping")
            continue

        camp_id, msg_id, camp_channel = camp_info.get(seg_name, (None, None, "in_app_popup"))
        count = profile["count"]
        print(f"  → {seg_name}: inserting {count} users …")

        for i in range(count):
            global_counter += 1
            display_name, email = rand_name(global_counter)

            # Behavioral parameters for this user
            n_sessions  = random.randint(*profile["sessions"])
            n_exports   = random.randint(*profile["exports"])
            n_paywall   = random.randint(*profile["paywall"])
            n_thesaurus = random.randint(*profile["thesaurus"])
            last_active_days_ago = random.uniform(*profile["days_ago"])
            created_days_ago     = random.uniform(60, 180)

            # ── users ──────────────────────────────────────────────────────────
            # Insert with zeroed aggregates — DB triggers keep them accurate
            # as we insert session_events, tool_usage_logs, paywall_events below.
            user_id = new_id()
            cur.execute("""
                INSERT INTO users (
                    user_id, email, display_name, plan, status,
                    created_at, last_login_at, days_since_last_login,
                    total_sessions, total_exports, total_paywall_hits, total_thesaurus_uses
                ) VALUES (%s,%s,%s,'free','active',%s,%s,%s, 0,0,0,0)
            """, (
                user_id, email, display_name,
                rand_ts(created_days_ago, created_days_ago + 1),
                rand_ts(last_active_days_ago, last_active_days_ago + 0.5),
                int(last_active_days_ago),
            ))

            # ── user_segments ──────────────────────────────────────────────────
            session_freq      = round(n_sessions / 30.0, 2)
            paywall_per_week  = round(n_paywall  /  4.0, 2)
            thesaurus_depth   = round(n_thesaurus / max(n_sessions, 1), 2)
            cur.execute("""
                INSERT INTO user_segments (
                    assignment_id, user_id, segment_id,
                    feature_session_frequency, feature_thesaurus_depth,
                    feature_paywall_hits_per_week, feature_export_count,
                    kmeans_distance
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                new_id(), user_id, seg_id,
                session_freq, thesaurus_depth,
                paywall_per_week, n_exports,
                round(random.uniform(0.1, 2.5), 6),
            ))

            # ── session_events ─────────────────────────────────────────────────
            # Sessions are spread from created_days_ago → last_active_days_ago.
            # trg_session_insert updates total_sessions + last_login_at automatically.
            session_ids = []
            for s_idx in range(n_sessions):
                sess_id  = new_id()
                started  = rand_ts(last_active_days_ago, created_days_ago)
                duration = random.randint(120, 3600)
                ended    = started + timedelta(seconds=duration)
                cur.execute("""
                    INSERT INTO session_events (
                        session_id, user_id, started_at, ended_at,
                        duration_seconds, word_count, line_count
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    sess_id, user_id, started, ended, duration,
                    random.randint(50, 1200), random.randint(5, 80),
                ))
                session_ids.append((sess_id, started))

            if not session_ids:
                continue

            # ── tool_usage_logs ────────────────────────────────────────────────
            # trg_tool_usage_insert updates total_exports + total_thesaurus_uses.
            thesaurus_budget = n_thesaurus
            export_budget    = n_exports
            misc_budget      = max(0, n_sessions // 2)

            entries = (
                [("thesaurus", 1)] * thesaurus_budget +
                [("export",    1)] * export_budget +
                [(random.choice(["rhyme", "meter", "synonym"]), 1)] * misc_budget
            )
            random.shuffle(entries)

            for t_idx, (tool, qcount) in enumerate(entries):
                sess_id, sess_ts = session_ids[t_idx % len(session_ids)]
                blocked = (
                    tool in ("thesaurus", "export")
                    and n_paywall > 0
                    and random.random() < 0.3
                )
                cur.execute("""
                    INSERT INTO tool_usage_logs (
                        log_id, session_id, user_id, tool,
                        query_count, synonym_depth, feature_blocked, used_at
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    new_id(), sess_id, user_id, tool,
                    qcount, random.randint(0, 3), blocked,
                    sess_ts + timedelta(minutes=random.randint(1, 30)),
                ))

            # ── paywall_events ─────────────────────────────────────────────────
            # trg_paywall_insert updates total_paywall_hits automatically.
            paywall_sessions = random.sample(
                session_ids, min(n_paywall, len(session_ids))
            )
            for sess_id, sess_ts in paywall_sessions:
                tool = random.choice(["thesaurus", "export"])
                cur.execute("""
                    INSERT INTO paywall_events (
                        event_id, user_id, session_id, tool,
                        feature_blocked, hit_at
                    ) VALUES (%s,%s,%s,%s,%s,%s)
                """, (
                    new_id(), user_id, sess_id, tool,
                    f"{tool}_limit_reached",
                    sess_ts + timedelta(minutes=random.randint(5, 45)),
                ))

            # ── notification_events ───────────────────────────────────────────
            if camp_id and msg_id and random.random() < 0.6:
                for _ in range(random.randint(1, 3)):
                    cur.execute("""
                        INSERT INTO notification_events (
                            notification_id, user_id, campaign_id, message_id,
                            event_type, channel, occurred_at
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        new_id(), user_id, camp_id, msg_id,
                        random.choice(NOTIF_EVENTS),
                        camp_channel,
                        rand_ts(0, 30),
                    ))

            # ── conversion_outcomes ────────────────────────────────────────────
            # trg_conversion_upgrade sets plan='pro' automatically on insert.
            if camp_id and msg_id and random.random() < CONVERSION_RATE:
                cur.execute("""
                    INSERT INTO conversion_outcomes (
                        conversion_id, user_id, campaign_id, message_id,
                        decision, plan_subscribed,
                        churned_within_30d, revenue_amd, converted_at
                    ) VALUES (%s,%s,%s,%s,'upgraded','pro',%s,%s,%s)
                """, (
                    new_id(), user_id, camp_id, msg_id,
                    random.random() < CHURN_30D_RATE,
                    2900.0,
                    rand_ts(0, 60),
                ))

            total_inserted += 1

        # Commit after each segment so progress is saved incrementally
        conn.commit()
        print(f"    ✅ {count} users committed")

    # ── Fix days_since_last_login ──────────────────────────────────────────────
    # The session trigger sets this to 0 on every insert (assumes live events).
    # Recalculate from last_login_at so dormant users show correct staleness.
    print("  → Recalculating days_since_last_login …")
    cur.execute("""
        UPDATE users
        SET days_since_last_login =
            GREATEST(0, EXTRACT(EPOCH FROM (now() - last_login_at)) / 86400)::INT
        WHERE last_login_at IS NOT NULL
    """)
    conn.commit()

    # ── Row count summary ─────────────────────────────────────────────────────
    print("\n--- Final Row Counts ---")
    tables = [
        "users", "user_segments", "session_events",
        "tool_usage_logs", "paywall_events",
        "notification_events", "conversion_outcomes",
        "segments", "campaigns", "message_templates", "global_params",
    ]
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        icon = "✅" if count > 0 else "⚠️ "
        print(f"  {icon}  {table}: {count} rows")

    cur.close()
    conn.close()
    print(f"\n✅ Done — {total_inserted} users seeded with full behavioral data.")


if __name__ == "__main__":
    main()
