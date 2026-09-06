# mc-behavioral-cheat-detection

Work in progress

Building a labeled Minecraft cheat detection dataset from a
self-hosted server, then using it to train and evaluate behavioral detection
models (killaura, reach, autoclicker, speed/fly).

## Status

- [x] Server + collector plugin (movement, combat, click telemetry)
- [ ] Data collection
- [ ] Feature engineering
- [ ] Modeling
- [ ] Dashboard
- [ ] Writeup

## Stack

Java (Spigot plugin) → Python (pandas, scikit-learn, LightGBM) → Streamlit

More soon.