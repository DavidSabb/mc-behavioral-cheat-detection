# Minecraft Behavioral Cheat Detection

Work in progress

Building a Minecraft cheat detection to detect cheat clients (killaura, reach, autoclicker) from gameplay telemetry using a dataset I generated myself on a private server

## Status

- [x] Server + collector plugin (movement, combat, click telemetry)
- [x] Data collection
- [x] Feature engineering
- [X] Modeling
- [ ] Dashboard
- [ ] Writeup

## Methods

The server logs how the player moves, aims and clicks during recorded sessions. Every log for hits also records the attacker's ping so that lag doesn't get mistaken for extra reach

From that raw data I look for patterns humans and cheats produce differently:

- **Aim**: Real mouse movement is in small fixed steps. Aim assist cheats' rotation patterns looks different since theirs move in bigger steps
- **Clicking**: speed is mostly irrelevant since a fast human's clicks looks very similar to autoclickers. The rhythm between clicks is whats important to notice
- **Reach**: it is measured to the nearest point of the hitbox, not the center so that its not skewed by which side you hit
- **Movement**: Minecraft's speed is predictable so I check how far movement strays from what it should be

## Stack

Java (Spigot), Python (pandas, scikit-learn, LightGBM), Streamlit (dashboard)

## Notes

- Rotation calculation had a bug that lead to every session having almost the same exact value. The way I was combining values slowly eroded the result near to zero. Fixed by comparing values in pairs and taking the middle one instead
- A logging bug that lead to combat hit logs not being written to the file for several sessions
  
More soon