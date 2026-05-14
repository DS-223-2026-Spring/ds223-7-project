"""
Pulse — K-Means Segmentation Pipeline
Data Scientist: Silva Vardanyan

Replaces the rule-based assign_segment() with a data-driven K-Means approach.

What this script does:
    1. Loads behavioral features from v_user_behavioral_features
    2. Scales features (median impute → StandardScaler)
    3. Fits K-Means with k=4 clusters
    4. Maps each cluster to a named segment by inspecting centroids:
           dormant  — highest days_since_last_login
           power    — highest total_exports + total_paywall_hits
           growing  — highest sessions_per_week (from remaining)
           casual   — the leftover cluster
    5. Expires existing user_segments rows and inserts new assignments
    6. Saves the fitted pipeline to outputs/kmeans_model.pkl for reuse

Run inside Docker:
    docker-compose exec ds python segment_kmeans.py

Or locally (DB must be reachable on port 5433):
    python segment_kmeans.py

Re-running is safe — old assignments are expired before new ones are inserted.
"""

import os
import pickle
import warnings

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@db:5432/pulse",
)

OUTPUT_DIR  = "outputs"
MODEL_PATH  = os.path.join(OUTPUT_DIR, "kmeans_model.pkl")
N_CLUSTERS  = 4
RANDOM_STATE = 42

# Features used for clustering
# Note: avg_synonym_depth is excluded — the column exists in the view but
# contains no observed values (all NULL), so it carries zero signal.
CLUSTER_FEATURES = [
    "total_sessions",
    "total_exports",
    "total_paywall_hits",
    "total_thesaurus_uses",
    "days_since_last_login",
    "sessions_per_week",
    "paywall_hits_last_7d",
]


# ── DB helpers ─────────────────────────────────────────────────────────────────

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def load_behavioral_features() -> pd.DataFrame:
    """Load v_user_behavioral_features — one row per free-tier user."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(
            text("SELECT * FROM v_user_behavioral_features"),
            conn,
        )


# ── K-Means pipeline ───────────────────────────────────────────────────────────

def build_kmeans_pipeline() -> Pipeline:
    """Return an unfitted sklearn Pipeline: imputer → scaler → KMeans."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("kmeans",  KMeans(
            n_clusters=N_CLUSTERS,
            random_state=RANDOM_STATE,
            n_init=20,          # more restarts → more stable centroids
            max_iter=500,
        )),
    ])


def map_clusters_to_segments(pipeline: Pipeline, feature_names: list[str]) -> dict[int, str]:
    """Inspect cluster centroids (in original scale) and name each cluster.

    Naming logic (applied in order — each cluster can only win once):
        1. dormant  — highest days_since_last_login centroid
        2. power    — highest (total_exports + total_paywall_hits) centroid
        3. growing  — highest sessions_per_week centroid
        4. casual   — the remaining cluster

    Returns a dict: {cluster_id: segment_name}
    """
    scaler  = pipeline.named_steps["scaler"]
    kmeans  = pipeline.named_steps["kmeans"]

    # Inverse-transform centroids back to original feature scale
    centroids_scaled = kmeans.cluster_centers_
    centroids = scaler.inverse_transform(centroids_scaled)
    df_c = pd.DataFrame(centroids, columns=feature_names)

    mapping: dict[int, str] = {}
    remaining = list(range(N_CLUSTERS))

    # 1. Dormant — most inactive
    dormant_idx = df_c.loc[remaining, "days_since_last_login"].idxmax()
    mapping[dormant_idx] = "dormant"
    remaining.remove(dormant_idx)

    # 2. Power — heavy exporter hitting limits
    df_c["_power_score"] = df_c["total_exports"] + df_c["total_paywall_hits"]
    power_idx = df_c.loc[remaining, "_power_score"].idxmax()
    mapping[power_idx] = "power"
    remaining.remove(power_idx)

    # 3. Growing — highest session frequency
    growing_idx = df_c.loc[remaining, "sessions_per_week"].idxmax()
    mapping[growing_idx] = "growing"
    remaining.remove(growing_idx)

    # 4. Casual — whatever is left
    mapping[remaining[0]] = "casual"

    print("\n  Cluster → Segment mapping:")
    for cid, name in sorted(mapping.items()):
        row = df_c.loc[cid]
        print(
            f"    Cluster {cid} → {name:<8}  "
            f"days_inactive={row['days_since_last_login']:.1f}  "
            f"exports={row['total_exports']:.1f}  "
            f"paywall_hits={row['total_paywall_hits']:.1f}  "
            f"sessions/wk={row['sessions_per_week']:.2f}"
        )

    return mapping


def run_kmeans(df: pd.DataFrame) -> tuple[Pipeline, np.ndarray, dict[int, str]]:
    """Fit K-Means on the behavioral features and return (pipeline, labels, mapping).

    Parameters
    ----------
    df : DataFrame from load_behavioral_features()

    Returns
    -------
    pipeline   : fitted sklearn Pipeline
    labels     : array of cluster IDs, one per user (same order as df)
    mapping    : {cluster_id: segment_name}
    """
    available = [c for c in CLUSTER_FEATURES if c in df.columns]
    missing   = set(CLUSTER_FEATURES) - set(available)
    if missing:
        print(f"  Warning: missing features {missing} — they will be imputed as median")

    X = df[available].values.astype(float)

    pipeline = build_kmeans_pipeline()
    labels   = pipeline.fit_predict(X)
    mapping  = map_clusters_to_segments(pipeline, available)

    return pipeline, labels, mapping


# ── Persistence ────────────────────────────────────────────────────────────────

def save_kmeans_model(pipeline: Pipeline, path: str = MODEL_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"\n  Model saved → {path}")


def load_kmeans_model(path: str = MODEL_PATH) -> Pipeline:
    with open(path, "rb") as f:
        return pickle.load(f)


# ── DB write ───────────────────────────────────────────────────────────────────

def write_segments_to_db(df: pd.DataFrame, segment_col: str = "segment_name") -> None:
    """Expire old user_segments rows and insert the new K-Means assignments.

    Steps:
        1. Expire all currently-active rows (expires_at = now())
        2. Look up segment_id for each named segment
        3. Insert one new row per user into user_segments

    Safe to re-run — each run expires the previous batch before inserting.
    """
    engine = get_engine()

    with engine.begin() as conn:
        # Step 1 — expire all active assignments
        conn.execute(text("""
            UPDATE user_segments
               SET expires_at = now()
             WHERE expires_at IS NULL
        """))
        print("  Expired previous user_segment assignments")

        # Step 2 — load segment name → segment_id map
        seg_rows = conn.execute(text("SELECT segment_id, name FROM segments")).mappings().all()
        seg_map  = {r["name"]: r["segment_id"] for r in seg_rows}

        # Step 3 — insert new assignments
        inserted = 0
        for _, row in df.iterrows():
            seg_name = row[segment_col]
            seg_id   = seg_map.get(seg_name)
            if seg_id is None:
                print(f"  Warning: unknown segment '{seg_name}' for user {row['user_id']} — skipped")
                continue
            conn.execute(text("""
                INSERT INTO user_segments (user_id, segment_id)
                VALUES (:uid, :sid)
            """), {"uid": str(row["user_id"]), "sid": str(seg_id)})
            inserted += 1

        print(f"  Inserted {inserted:,} new user_segment rows")


# ── Summary ────────────────────────────────────────────────────────────────────

def print_segment_summary(df: pd.DataFrame, segment_col: str = "segment_name") -> None:
    counts = df[segment_col].value_counts()
    total  = len(df)
    print("\n  Segment distribution:")
    for seg in ["power", "growing", "casual", "dormant"]:
        n   = counts.get(seg, 0)
        pct = n / total * 100
        print(f"    {seg:<10} {n:>4}  ({pct:.1f}%)")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — K-Means Segmentation Pipeline")
    print("=" * 65)

    print("\n[1/4] Loading behavioral features …")
    df = load_behavioral_features()
    print(f"  {len(df):,} users loaded")

    print("\n[2/4] Fitting K-Means (k=4) …")
    pipeline, labels, mapping = run_kmeans(df)

    df["segment_name"] = [mapping[lbl] for lbl in labels]
    print_segment_summary(df)

    print("\n[3/4] Saving model …")
    save_kmeans_model(pipeline)

    print("\n[4/4] Writing assignments to DB …")
    write_segments_to_db(df)

    print("\n" + "=" * 65)
    print("  K-Means segmentation complete.")
    print("  Model : outputs/kmeans_model.pkl")
    print("  Table : user_segments (active rows updated)")
    print("=" * 65)
