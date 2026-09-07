import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
def wrap_degrees(series):
    """Wrap angle differences into [-180, 180].

    Yaw is reported in degrees and wraps at the boundary. A turn from
    179 to -179 is a 2 degree movement, but a naive diff reports -358.
    Every rotation feature depends on getting this right.
    """
    return (series + 180) % 360 - 180


def load_sessions():
    s = pd.read_csv(RAW / "sessions.csv")
    s = s[s.label != "UNLABELED"].copy()
    s["duration_s"] = (s.ended_ts - s.started_ts) / 1000
    s["is_cheat"] = (s.label != "LEGIT").astype(int)
    return s


def load_movement(sessions):
    m = pd.read_csv(RAW / "movement.csv")
    m = m[m.session_id.isin(sessions.session_id)].copy()
    m = m.sort_values(["session_id", "ts"]).reset_index(drop=True)

    g = m.groupby("session_id")
    m["dt"]    = g.ts.diff()
    m["dx"]    = g.x.diff()
    m["dy"]    = g.y.diff()
    m["dz"]    = g.z.diff()
    m["dyaw"]  = wrap_degrees(g.yaw.diff())
    m["dpitch"] = g.pitch.diff()

    m["speed_h"] = np.hypot(m.dx, m.dz)
    m["accel_h"] = m.groupby("session_id").speed_h.diff()

    return m


def load_combat(sessions):
    c = pd.read_csv(RAW / "combat.csv")
    c = c[c.session_id.isin(sessions.session_id)].copy()
    c = c.sort_values(["session_id", "ts"])
    c["since_last_ms"] = c.groupby("session_id").ts.diff()
    return c


def load_clicks(sessions):
    k = pd.read_csv(RAW / "clicks.csv")
    k = k[k.session_id.isin(sessions.session_id)].copy()
    k = k.sort_values(["session_id", "ts"])
    k["interval_ms"] = k.groupby("session_id").ts.diff()
    return k
