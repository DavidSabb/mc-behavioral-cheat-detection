import pandas as pd
import numpy as np
from sklearn.metrics import (precision_recall_curve, average_precision_score, precision_score, recall_score, confusion_matrix)
import matplotlib.pyplot as plt

def evaluate(y_true, y_prob):
    prec, rec, thr = precision_recall_curve(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)

    rows = []
    for t in [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]:
        pred = (y_prob >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
        rows.append({
            "threshold": t,
            "precision": tp / (tp + fp) if tp + fp else np.nan,
            "recall": tp / (tp + fn),
            "fpr": fp / (fp + tn),
            "flagged": pred.sum()
        })
    return ap, pd.DataFrame(rows)

def recall_by_type(X, y_prob, threshold):
    out = []
    for label in X.label.unique():
        if label == "LEGIT":
            continue
        mask = X.label == label
        out.append({
            "cheat": label,
            "n": mask.sum(),
            "recall": (y_prob[mask] >= threshold).mean(),
        })
    return pd.DataFrame(out)

def plot_pr_curve(y_true, y_prob, label="model"):
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(rec, prec, label=label)
    ax.set_xlabel("recall")
    ax.set_ylabel("precision")
    ax.set_title("Precision-Recall Curve")
    ax.legend()
    return fig


def ablation(X, features, train_fn, drop_groups: dict):
    """Retrain with feature groups removed, report AP for each.
    drop_groups = {"rotation": ["yaw_gcd", "yaw_std", ...], ...}
    """
    results = {}
    y = X.is_cheat.values

    oof_full, _ = train_fn(X, features)
    results["full"] = average_precision_score(y, oof_full)

    for name, cols in drop_groups.items():
        remaining = [f for f in features if f not in cols]
        oof_dropped, _ = train_fn(X, remaining)
        results[f"no_{name}"] = average_precision_score(y, oof_dropped)

    return pd.DataFrame(
        [{"removed": k, "ap": v} for k, v in results.items()]
    )