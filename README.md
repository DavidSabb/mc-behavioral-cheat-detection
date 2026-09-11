# mc-behavioral-cheat-detection

Work in progress

Building a labeled Minecraft cheat detection dataset from a
self-hosted server, then using it to train and evaluate behavioral detection
models (killaura, reach, autoclicker, speed/fly).

## Status

- [x] Server + collector plugin (movement, combat, click telemetry)
- [x] Data collection
- [x] Feature engineering
- [X] Modeling
- [ ] Dashboard
- [ ] Writeup

## Stack

Java (Spigot plugin) → Python (pandas, scikit-learn, LightGBM) → Streamlit

## Notes

- Found and fixed two real bugs during development: a floating-point
  GCD calculation that silently collapsed to a constant, and a missing
  write call that left combat data unlogged for several sessions.
- No feature leakage detected in SHAP analysis so far — top features
  are physically interpretable (click timing, rotation ratios), not
  session metadata.

More soon