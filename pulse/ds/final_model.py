"""
Pulse — Final Model: Best-Performing Conversion Predictor
Data Scientist: Silva Vardanyan

Trains and evaluates two candidate models for conversion prediction:
    1. Logistic Regression — tuned via GridSearchCV (C, solver, penalty)
    2. Random Forest       — tuned via GridSearchCV (n_estimators, max_depth)

Selection criterion: 5-fold stratified CV ROC-AUC (handles class imbalance).
The winner is saved to outputs/final_model.pkl for use by predict.py.

Run locally (DB must be reachable):
    python final_model.py

Output artifacts:
    outputs/final_model.pkl              — pickled Pipeline (scaler + best clf)
    outputs/final_model_metrics.txt      — evaluation report
    outputs/final_model_roc.png          — ROC curves for both models
    outputs/final_model_importance.png   — feature importance / coefficients
"""

import os
import pickle
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import (
    train_test_split, StratifiedKFold, GridSearchCV, cross_val_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, RocCurveDisplay,
    confusion_matrix, ConfusionMatrixDisplay,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Import the documented feature pipeline
from feature_pipeline import load_model_dataset, prepare_features, FEATURE_COLS

warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────────────────────────

RANDOM_STATE = 42
OUTPUT_DIR   = "outputs"
MODEL_PATH   = os.path.join(OUTPUT_DIR, "final_model.pkl")


# ── Model definitions with hyperparameter grids ────────────────────────────────

def _lr_pipeline() -> tuple[Pipeline, dict]:
    """Return LogisticRegression pipeline and its GridSearchCV param grid."""
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("clf",     LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=RANDOM_STATE,
        )),
    ])
    grid = {
        "clf__C":       [0.01, 0.1, 1.0, 10.0],
        "clf__solver":  ["lbfgs", "liblinear"],
        "clf__penalty": ["l2"],
    }
    return pipe, grid


def _rf_pipeline() -> tuple[Pipeline, dict]:
    """Return RandomForest pipeline and its GridSearchCV param grid."""
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("clf",     RandomForestClassifier(
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])
    grid = {
        "clf__n_estimators": [100, 200],
        "clf__max_depth":    [4, 6, None],
        "clf__min_samples_leaf": [1, 5],
    }
    return pipe, grid


# ── Training ───────────────────────────────────────────────────────────────────

def train_and_select(
    X_raw: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
) -> dict:
    """Train both models with GridSearchCV and return results for both.

    Uses 5-fold stratified CV to tune hyperparameters, then evaluates on a
    held-out 25% test set.  Returns a results dict with the winning model
    clearly marked.

    Parameters
    ----------
    X_raw        : np.ndarray — raw feature matrix (n_users × n_features)
    y            : np.ndarray — binary target
    feature_names: list[str]  — column names in same order as X_raw columns

    Returns
    -------
    dict keyed by model name, each value is a sub-dict with:
        pipeline, best_params, cv_roc_auc, test_roc_auc,
        y_test, y_pred, y_prob, report, is_winner
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    candidates = {
        "Logistic Regression": _lr_pipeline(),
        "Random Forest":       _rf_pipeline(),
    }

    results = {}
    for name, (pipe, grid) in candidates.items():
        print(f"\n── Tuning: {name} ──")
        search = GridSearchCV(
            pipe, grid,
            cv=cv,
            scoring="roc_auc",
            n_jobs=-1,
            refit=True,
        )
        search.fit(X_train, y_train)
        best_pipe = search.best_estimator_

        y_pred = best_pipe.predict(X_test)
        y_prob = best_pipe.predict_proba(X_test)[:, 1]
        cv_auc  = search.best_score_
        tst_auc = roc_auc_score(y_test, y_prob)

        print(f"  Best params  : {search.best_params_}")
        print(f"  CV ROC-AUC   : {cv_auc:.4f}")
        print(f"  Test ROC-AUC : {tst_auc:.4f}")
        print(classification_report(
            y_test, y_pred,
            target_names=["Not converted", "Converted"],
        ))

        results[name] = {
            "pipeline":    best_pipe,
            "best_params": search.best_params_,
            "cv_roc_auc":  round(cv_auc,  4),
            "test_roc_auc": round(tst_auc, 4),
            "X_test":  X_test,
            "y_test":  y_test,
            "y_pred":  y_pred,
            "y_prob":  y_prob,
            "report":  classification_report(
                y_test, y_pred,
                target_names=["Not converted", "Converted"],
                output_dict=True,
            ),
            "is_winner": False,
        }

    # Mark the winner by CV ROC-AUC
    winner_name = max(results, key=lambda k: results[k]["cv_roc_auc"])
    results[winner_name]["is_winner"] = True
    print(f"\n★ WINNER: {winner_name} "
          f"(CV AUC = {results[winner_name]['cv_roc_auc']:.4f})")

    return results


def get_feature_importance(results: dict, feature_names: list[str]) -> dict:
    """Extract feature importances / coefficients from both fitted models.

    Returns a dict: model_name → pd.Series of importance values.
    """
    out = {}
    for name, r in results.items():
        clf = r["pipeline"].named_steps["clf"]
        if hasattr(clf, "coef_"):
            imp = pd.Series(
                clf.coef_[0], index=feature_names
            ).abs().sort_values(ascending=False)
        elif hasattr(clf, "feature_importances_"):
            imp = pd.Series(
                clf.feature_importances_, index=feature_names
            ).sort_values(ascending=False)
        else:
            imp = pd.Series(dtype=float)
        out[name] = imp
    return out


# ── Persistence ────────────────────────────────────────────────────────────────

def save_model(pipeline: Pipeline, path: str = MODEL_PATH) -> None:
    """Pickle the winning pipeline to *path*."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"\n✓ Model saved to: {path}")


def load_model(path: str = MODEL_PATH) -> Pipeline:
    """Load a pickled pipeline from *path*."""
    with open(path, "rb") as f:
        return pickle.load(f)


# ── Plotting ───────────────────────────────────────────────────────────────────

def plot_roc_curves(results: dict, save_dir: str = OUTPUT_DIR) -> None:
    """Side-by-side ROC curves for all trained models."""
    os.makedirs(save_dir, exist_ok=True)
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, (name, r) in zip(axes, results.items()):
        label = f"{'★ ' if r['is_winner'] else ''}{name} (AUC = {r['test_roc_auc']:.3f})"
        RocCurveDisplay.from_predictions(
            r["y_test"], r["y_prob"],
            name=label, ax=ax,
            color="#00b87a" if r["is_winner"] else "#9ca3af",
        )
        ax.plot([0, 1], [0, 1], "k--", lw=1)
        ax.set_title(f"{'[WINNER] ' if r['is_winner'] else ''}{name}")

    fig.suptitle("Pulse — Final Model ROC Curves", fontsize=13, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(save_dir, "final_model_roc.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
    plt.close(fig)


def plot_feature_importance(
    importances: dict, save_dir: str = OUTPUT_DIR
) -> None:
    """Horizontal bar charts of feature importance for each model."""
    os.makedirs(save_dir, exist_ok=True)
    n = len(importances)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, (name, imp) in zip(axes, importances.items()):
        if imp.empty:
            ax.set_title(f"{name}\n(no importance available)")
            continue
        colors = ["#00b87a" if i == 0 else "#3b82f6" for i in range(len(imp))]
        ax.barh(imp.index[::-1], imp.values[::-1], color=colors[::-1], height=0.6)
        ax.set_title(f"{name}\nFeature Importance")
        ax.set_xlabel("Importance (abs. coef / Gini)")

    fig.suptitle("Pulse — Feature Importance", fontsize=13, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(save_dir, "final_model_importance.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
    plt.close(fig)


# ── Text report ────────────────────────────────────────────────────────────────

def write_metrics_report(
    results: dict,
    importances: dict,
    feature_names: list[str],
    save_dir: str = OUTPUT_DIR,
) -> str:
    """Write a human-readable metrics report and return its path."""
    os.makedirs(save_dir, exist_ok=True)
    lines = [
        "=" * 65,
        "  PULSE — FINAL MODEL METRICS REPORT",
        "  Data Scientist: Silva Vardanyan",
        "=" * 65,
        "",
        f"  Features used ({len(feature_names)}): {feature_names}",
        "",
    ]

    for name, r in results.items():
        tag = " ★ WINNER" if r["is_winner"] else ""
        lines += [
            f"── {name}{tag} ──",
            f"  Best params  : {r['best_params']}",
            f"  CV ROC-AUC   : {r['cv_roc_auc']:.4f}",
            f"  Test ROC-AUC : {r['test_roc_auc']:.4f}",
            "",
        ]
        if name in importances and not importances[name].empty:
            lines.append("  Feature importance (top 5):")
            for feat, val in importances[name].head(5).items():
                lines.append(f"    {feat:<34} {val:.4f}")
            lines.append("")

    path = os.path.join(save_dir, "final_model_metrics.txt")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved {path}")
    return path


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  Pulse — Final Model Training")
    print("=" * 65)

    # Load data via the feature pipeline
    df = load_model_dataset()
    X_raw, y, available = prepare_features(df)

    print(f"\nDataset: {len(df):,} users  "
          f"| positive rate: {y.mean():.2%} ({y.sum()} converted)\n")

    # Train and select
    results = train_and_select(X_raw, y, available)

    # Save the winning model
    winner_name = next(n for n, r in results.items() if r["is_winner"])
    save_model(results[winner_name]["pipeline"])

    # Feature importance
    importances = get_feature_importance(results, available)

    print("\nTop predictors (winner model):")
    if winner_name in importances:
        for feat, val in importances[winner_name].head(5).items():
            print(f"  {feat:<34} {val:.4f}")

    # Plots and report
    plot_roc_curves(results)
    plot_feature_importance(importances)
    write_metrics_report(results, importances, available)

    print("\n✓ Final model training complete.")
