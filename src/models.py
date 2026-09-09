import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

def get_feature_cols(X):
    return [c for c in X.columns if c not in (
        "window_id", "session_id", "label", "player", "is_cheat")]

def rule_baseline(X):
    flags = pd.DataFrame(index=X.index)
    flags["reach"]       = (X["reach_p95"] > 3.05) if "reach_p95" in X.columns else pd.Series(False, index=X.index)
    flags["autoclicker"] = (X["iv_cv"] < 0.10) if "iv_cv" in X.columns else pd.Series(False, index=X.index)
    flags["speed"]       = (X["speed_resid_max"] > 0.05) if "speed_resid_max" in X.columns else pd.Series(False, index=X.index)
    flags["aim"]         = (X["yaw_gcd"] < 1e-3) if "yaw_gcd" in X.columns else pd.Series(False, index=X.index)
    return flags.any(axis=1).astype(int)

def train_cv(X, group_col="session_id"):
    FEATURES = get_feature_cols(X)
    y = X.is_cheat.values
    groups = X[group_col].values
    oof = np.zeros(len(X))
    models = []

    for tr, te in GroupKFold(n_splits=5).split(X, y, groups):
        model = lgb.LGBMClassifier(
            n_estimators=400,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            random_state=42
        )
        model.fit(X.iloc[tr][FEATURES], y[tr])
        oof[te] = model.predict_proba(X.iloc[te][FEATURES])[:, 1]
        models.append(model)
    return oof, models

def novelty_test(X, held_out_cheat):
    FEATURES = get_feature_cols(X)
    train = X[(X.label == "LEGIT")]
    test = X[(X.label == "LEGIT") | (X.label == held_out_cheat)]

    pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        IsolationForest(contamination=0.05, random_state=42),
    )
    pipe.fit(train[FEATURES])
    scores = -pipe.decision_function(test[FEATURES])
    return test, scores

def plot_calibration(y_true, y_prob):
    frac_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=10)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(mean_pred, frac_pos, "o--", label="model")
    ax.plot([0, 1], [0, 1], "k--", label="perfect")
    ax.set_xlabel("predicted probability")
    ax.set_ylabel("observed frequency")
    ax.legend()
    return fig

