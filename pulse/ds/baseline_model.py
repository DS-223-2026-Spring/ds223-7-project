"""
Pulse — Baseline Predictive Models
Data Scientist: Silva Vardanyan

Two baseline tasks:
    1. Conversion prediction  — logistic regression & decision tree to predict
                                whether a free-tier user will convert to Pro.
    2. Segment classification — decision tree to classify users into the four
                                behavioural segments (power/growing/casual/dormant).

Both models use only features available in v_user_behavioral_features and
conversion_outcomes, so they can be retrained whenever the DB is updated.

Run locally (with DB running):
    python baseline_model.py
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_auc_score,
    RocCurveDisplay,
)
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pulse_user:pulse_pass@localhost:5433/pulse",
)

RANDOM_STATE = 42

FEATURE_COLS = [
    "avg_sessions_per_week",
    "avg_exports_per_week",
    "avg_paywall_hits",
    "avg_thesaurus_uses",
    "days_since_last_login",
]

SEGMENT_ORDER = ["power", "growing", "casual", "dormant"]


# ── Data loading ──────────────────────────────────────────────────────

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def load_conversion_dataset() -> pd.DataFrame:
    """Join behavioral features with conversion outcomes for Task 1."""
    sql = """
        SELECT
            f.*,
            COALESCE(co.converted, FALSE)::int  AS converted,
            co.days_to_convert
        FROM v_user_behavioral_features f
        LEFT JOIN conversion_outcomes co USING (user_id)
        ORDER BY f.user_id
    """
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


def load_segment_dataset() -> pd.DataFrame:
    """Load behavioral features for Task 2 (segment classification)."""
    with get_engine().connect() as conn:
        return pd.read_sql(
            text("SELECT * FROM v_user_behavioral_features ORDER BY user_id"),
            conn,
        )


# ── Task 1: Conversion prediction ─────────────────────────────────────

def train_conversion_models(df: pd.DataFrame):
    """Train logistic regression and decision tree on conversion labels.

    Returns a dict with both fitted pipelines and their evaluation metrics.
    """
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].fillna(0)
    y = df["converted"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    LogisticRegression(max_iter=500, random_state=RANDOM_STATE)),
        ]),
        "Decision Tree": Pipeline([
            ("clf", DecisionTreeClassifier(max_depth=4, random_state=RANDOM_STATE)),
        ]),
    }

    results = {}
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]
        cv_auc  = cross_val_score(pipe, X, y, cv=cv, scoring="roc_auc").mean()

        results[name] = {
            "pipeline":   pipe,
            "X_test":     X_test,
            "y_test":     y_test,
            "y_pred":     y_pred,
            "y_prob":     y_prob,
            "roc_auc_cv": round(cv_auc, 4),
            "roc_auc":    round(roc_auc_score(y_test, y_prob), 4),
            "report":     classification_report(y_test, y_pred, output_dict=True),
        }
        print(f"\n── {name} ──")
        print(f"  CV ROC-AUC : {results[name]['roc_auc_cv']:.4f}")
        print(f"  Test ROC-AUC: {results[name]['roc_auc']:.4f}")
        print(classification_report(y_test, y_pred, target_names=["Not converted", "Converted"]))

    return results


def plot_conversion_results(results: dict, save_dir: str = "."):
    """Confusion matrices and ROC curves for conversion models."""
    os.makedirs(save_dir, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("Conversion Prediction — Baseline Models", fontsize=14, fontweight="bold")

    names = list(results.keys())
    for col, name in enumerate(names):
        r = results[name]
        # Confusion matrix
        cm = confusion_matrix(r["y_test"], r["y_pred"])
        disp = ConfusionMatrixDisplay(cm, display_labels=["Not conv.", "Converted"])
        disp.plot(ax=axes[0, col], colorbar=False, cmap="Blues")
        axes[0, col].set_title(f"{name}\nConfusion Matrix")

        # ROC curve
        RocCurveDisplay.from_predictions(
            r["y_test"], r["y_prob"],
            name=f"AUC = {r['roc_auc']:.3f}",
            ax=axes[1, col],
            color="#3b82f6",
        )
        axes[1, col].plot([0, 1], [0, 1], "k--", lw=1)
        axes[1, col].set_title(f"{name}\nROC Curve")

    fig.tight_layout()
    path = os.path.join(save_dir, "conversion_model_results.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
    plt.show()


def plot_feature_importance(results: dict, feature_names: list, save_dir: str = "."):
    """Bar chart of feature importance from the Decision Tree model."""
    os.makedirs(save_dir, exist_ok=True)
    tree_pipe = results["Decision Tree"]["pipeline"]
    clf       = tree_pipe.named_steps["clf"]
    imp       = pd.Series(clf.feature_importances_, index=feature_names).sort_values()

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#3b82f6" if v >= 0 else "#9ca3af" for v in imp.values]
    ax.barh(imp.index, imp.values, color=colors)
    ax.set_title("Decision Tree — Feature Importance (Conversion)")
    ax.set_xlabel("Importance")
    ax.axvline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    path = os.path.join(save_dir, "feature_importance.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
    plt.show()


# ── Task 2: Segment classification ───────────────────────────────────

def train_segment_classifier(df: pd.DataFrame):
    """Train a decision tree to classify users into the 4 segments.

    Returns the fitted model and evaluation metrics.
    """
    le = LabelEncoder()
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].fillna(0)
    y = le.fit_transform(df["segment"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    clf = DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_acc = cross_val_score(clf, X, y, cv=cv, scoring="accuracy").mean()

    print("\n── Segment Classifier (Decision Tree) ──")
    print(f"  CV Accuracy : {cv_acc:.4f}")
    print(classification_report(
        y_test, y_pred,
        target_names=le.classes_,
    ))

    # Text summary of tree rules
    rules = export_text(clf, feature_names=available, max_depth=3)
    print("\nTop 3 levels of decision rules:")
    print(rules)

    return {
        "clf":        clf,
        "encoder":    le,
        "features":   available,
        "X_test":     X_test,
        "y_test":     y_test,
        "y_pred":     y_pred,
        "cv_accuracy": round(cv_acc, 4),
        "report":     classification_report(y_test, y_pred,
                                             target_names=le.classes_,
                                             output_dict=True),
    }


def plot_segment_confusion(result: dict, save_dir: str = "."):
    """Confusion matrix for segment classifier."""
    os.makedirs(save_dir, exist_ok=True)
    labels = result["encoder"].classes_
    cm     = confusion_matrix(result["y_test"], result["y_pred"])
    disp   = ConfusionMatrixDisplay(cm, display_labels=labels)

    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, colorbar=False, cmap="Greens")
    ax.set_title(f"Segment Classifier — Confusion Matrix\nCV Accuracy: {result['cv_accuracy']:.4f}")
    fig.tight_layout()
    path = os.path.join(save_dir, "segment_classifier_cm.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
    plt.show()


# ── Summary ───────────────────────────────────────────────────────────

def print_model_comparison(conv_results: dict, seg_result: dict):
    """Print a concise comparison table of all baseline models."""
    rows = []
    for name, r in conv_results.items():
        rep = r["report"]
        rows.append({
            "Task":       "Conversion",
            "Model":      name,
            "Metric":     "ROC-AUC",
            "CV Score":   r["roc_auc_cv"],
            "Test Score": r["roc_auc"],
        })
    rows.append({
        "Task":       "Segmentation",
        "Model":      "Decision Tree",
        "Metric":     "Accuracy",
        "CV Score":   seg_result["cv_accuracy"],
        "Test Score": round(
            sum(v for k, v in seg_result["report"].items()
                if isinstance(v, dict) and "precision" in v) /
            max(1, len([k for k, v in seg_result["report"].items()
                        if isinstance(v, dict) and "precision" in v])),
            4,
        ),
    })
    print("\n── Baseline Model Comparison ──")
    print(pd.DataFrame(rows).to_string(index=False))


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Conversion Prediction ===")
    conv_df      = load_conversion_dataset()
    conv_results = train_conversion_models(conv_df)

    available_feats = [c for c in FEATURE_COLS if c in conv_df.columns]
    plot_conversion_results(conv_results, save_dir="outputs")
    plot_feature_importance(conv_results, available_feats, save_dir="outputs")

    print("\n=== Segment Classification ===")
    seg_df     = load_segment_dataset()
    seg_result = train_segment_classifier(seg_df)
    plot_segment_confusion(seg_result, save_dir="outputs")

    print_model_comparison(conv_results, seg_result)
