import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Anticheat Review", layout="wide")

@st.cache_data
def load():
    X = pd.read_parquet("data/processed/features.parquet")
    X["risk"] = np.load("data/processed/oof_scores.npy")
    return X

X = load()

tab1, tab2 = st.tabs(["Review queue", "Population"])

with tab1:
    threshold = st.slider("Risk threshold", 0.0, 1.0, 0.90, 0.01)

    per_player = (X.groupby(["player", "session_id", "label"])
                   .agg(mean_risk=("risk", "mean"),
                        max_risk=("risk", "max"),
                        flagged=("risk", lambda s: (s >= threshold).mean()),
                        windows=("risk", "size"))
                   .reset_index()
                   .sort_values("mean_risk", ascending=False))

    st.dataframe(per_player, use_container_width=True)

    sel = st.selectbox("Inspect session", per_player.session_id)
    s = X[X.session_id == sel].sort_values("window_id")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(
            px.line(s, y="risk", title=f"Risk over session {sel}")
              .add_hline(y=threshold, line_dash="dash"),
            use_container_width=True)

    with c2:
        st.metric("Ground truth", s.label.iloc[0])
        st.metric("Mean risk", f"{s.risk.mean():.3f}")

        # Deviation from the legitimate population, in standard deviations
        legit = X[X.label == "LEGIT"]
        key = ["iv_cv", "yaw_gcd", "reach_p95", "speed_resid_max"]
        dev = pd.DataFrame({
            "feature": key,
            "value":   [s[k].mean() for k in key],
            "z":       [(s[k].mean() - legit[k].mean()) / (legit[k].std() + 1e-9)
                        for k in key],
        }).sort_values("z", key=abs, ascending=False)
        st.write("**Deviation from legit baseline (σ)**")
        st.dataframe(dev, hide_index=True)

with tab2:
    st.plotly_chart(
        px.histogram(X, x="risk", color="label", barmode="overlay",
                     nbins=50, title="Risk distribution by ground truth"),
        use_container_width=True)

    by_type = (X.groupby("label")
                .agg(n=("risk", "size"), mean_risk=("risk", "mean"))
                .reset_index())
    st.dataframe(by_type, hide_index=True)