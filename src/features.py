import numpy as np
import pandas as pd
from scipy import stats

WINDOW_MS = 30_000
STEP_MS = 15_000
BASE_WALK   = 0.215
SPRINT_MULT = 1.30
SPEED_EFFECT_MULT = 0.20

def assign_windows(df):
    out = []
    sessions = df.groupby("session_id")
    print(f"Total sessions to process: {df.session_id.nunique()}")
    for sid, g in sessions:
        t0 = g.ts.min()
        rel = g.ts - t0
        n_windows = int(rel.max() // STEP_MS)
        print(f"  session {sid}: {len(g)} rows, {n_windows} windows")
        for i in range(n_windows):
            lo, hi = i * STEP_MS, i * STEP_MS + WINDOW_MS
            w = g[(rel >= lo) & (rel < hi)]
            if len(w) < 50:
                continue
            out.append((f"{sid}_w{i}", sid, w))
    return out

def gcd_float(a, b, eps=1e-4):
    a, b = abs(a), abs(b)
    while b > eps:
        a, b = b, a % b
    return a

def rotation_gcd(deltas, min_samples=40, eps=0.02):
    d = [abs(x) for x in deltas if abs(x) > eps]
    if len(d) < min_samples:
        return np.nan

    pair_gcds = [gcd_float(d[i], d[i + 1], eps) for i in range(len(d) - 1)]
    pair_gcds = [g for g in pair_gcds if g > eps]

    if not pair_gcds:
        return 0.0
    return float(np.median(pair_gcds))

def rotation_features(w):
    dyaw, dpitch = w.dyaw.dropna(), w.dpitch.dropna()
    active = dyaw[dyaw.abs() > 1e-6]

    return {
        "yaw_gcd": rotation_gcd(dyaw.values),
        "yaw_std": dyaw.std(),
        "yaw_kurtosis": stats.kurtosis(dyaw) if len(dyaw) > 3 else np.nan,
        "yaw_skew": stats.skew(dyaw) if len(dyaw) > 3 else np.nan,
        "yaw_max": dyaw.abs().max(),
        "yaw_p99": dyaw.abs().quantile(0.99),
        "yaw_pitch_ratio": dyaw.abs().mean() / (dpitch.abs().mean() + 1e-9),
        "pitch_zero_frac": (dpitch.abs() < 1e-6).mean(),
        "snap_count":      (dyaw.abs() > 30).sum(),
        "reversal_rate":   (np.diff(np.sign(active)) != 0).sum() / (len(w) / 20 + 1e-9),
    }

def click_features(intervals):
    iv = intervals.dropna()
    iv = iv[(iv > 5) & (iv < 2000)]
    if len(iv) < 20:
        return {}

    return {
        "cps_mean": 1000 / iv.mean(),
        "iv_std": iv.std(),
        "iv_cv": iv.std() / iv.mean(),
        "iv_kurtosis": stats.kurtosis(iv),
        "iv_skew": stats.skew(iv),
        "iv_min": iv.min(),
        "iv_unique_frac": iv.round().nunique() / len(iv),
        "iv_p95_p50": iv.quantile(0.95) / iv.median(),
        "iv_mean_median": iv.mean() / iv.median(),
    }

def reach_features(hits):
    if len(hits) < 5:
        return {}
    r = hits.reach
    return {
        "reach_mean": r.mean(),
        "reach_std": r.std(),
        "reach_p95": r.quantile(0.95),
        "reach_max": r.max(),
        "reach_over_30": (r > 3.0).mean(),
        "reach_over_29": (r > 2.9).mean(),
        "hit_rate": len(hits) / 30.0,
        "ping_mean": hits.attacker_ping.mean(),
    }

def movement_features(w):
    expected = (BASE_WALK * np.where(w.sprinting, SPRINT_MULT, 1.0) * (1 + SPEED_EFFECT_MULT * w.speed_amp))
    residual = w.speed_h - expected

    dy = w.dy.dropna()
    predicted_dy = dy.shift(1) * 0.98 - 0.08
    fall_resid = (dy - predicted_dy).dropna()

    return {
        "speed_resid_mean": residual.mean(),
        "speed_resid_max": residual.max(),
        "speed_resid_pos": (residual > 0.01).mean(),
        "speed_max": w.speed_h.max(),
        "airborne_frac": (~w.on_ground).mean(),
        "fall_resid_std": fall_resid.std(),
        "fall_resid_max": fall_resid.abs().max(),
        "air_const_y_frac": ((w.dy.abs() < 1e-4) & (~w.on_ground)).mean(),
    }

def build_feature_table(movement, combat, clicks, sessions):
    rows = []
    for win_id, sid, w in assign_windows(movement):
        lo, hi = w.ts.min(), w.ts.max()

        hits = combat[(combat.session_id == sid) &
                      combat.ts.between(lo, hi)]
        clk  = clicks[(clicks.session_id == sid) &
                      clicks.ts.between(lo, hi)]

        feats = {"window_id": win_id, "session_id": sid}
        feats.update(rotation_features(w))
        feats.update(movement_features(w))
        feats.update(reach_features(hits))
        feats.update(click_features(clk.interval_ms))
        rows.append(feats)

    X = pd.DataFrame(rows)
    meta = sessions.set_index("session_id")[["label", "player", "is_cheat"]]
    return X.join(meta, on="session_id")