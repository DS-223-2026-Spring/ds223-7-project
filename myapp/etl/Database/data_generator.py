import csv, os, random
from datetime import datetime, timedelta

def load_users_csv(path: str) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def generate_sample_users(n: int = 100) -> list[dict]:
    segments = ["power", "growing", "casual", "dormant"]
    plans = ["free", "pro"]
    users = []
    for i in range(n):
        users.append({
            "user_id": f"u{i:04d}",
            "plan": random.choice(plans),
            "segment": random.choice(segments),
            "created_at": datetime.now() - timedelta(days=random.randint(0, 365)),
        })
    return users
