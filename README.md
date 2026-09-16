# Minecraft Behavioral Cheat Detection

Work in progress

Building a Minecraft cheat detection to detect cheat clients (killaura, reach, autoclicker) from gameplay telemetry using a dataset I generated myself on a private server

## Results

Average Precision: **0.778**

| Threshold | Precision | Recall | False Positive Rate | Windows Flagged |
|---|---|---|---|---|
| 0.50 | 0.621 | 0.755 | 0.292 | 174 |
| 0.70 | 0.650 | 0.713 | 0.243 | 157 |
| 0.80 | 0.656 | 0.706 | 0.235 | 154 |
| 0.90 | 0.667 | 0.657 | 0.208 | 141 |
| 0.95 | 0.682 | 0.615 | 0.181 | 129 |
| 0.99 | 0.784 | 0.559 | 0.097 | 102 |

At threshold 0.90, recall by cheat type:

| Cheat | Sessions | Recall |
|---|---|---|
| Killaura/triggerbot | 44 windows | 1.00 |
| Autoclicker | 41 windows | 0.88 |
| Reach | 58 windows | 0.24 |

- Autoclicker and triggerbot detection is strong
- Reach detection is weak which was expected since its logging pipeline had a bug that was only fixed partway through data collection so it had the least mature signal of the three categories

## Feature Ablation

I retrained the model with each group of features removed to see what
it actually relies on:

| Removed | Avg Precision |
|---|---|
| nothing | 0.778 |
| rotation (aim) | 0.685 |
| click timing | 0.627 |
| reach | 0.818 |
| movement | 0.736 |

- Click timing matters the most. Removing it hurts the score the most
- Reach barely moves the needle which lines up with the recall numbers

## The data

~3 hours across 22 labeled sessions, all self-collected. I know
exactly what was happening in every session because I set it up myself.

| Label | Sessions |
|---|---|
| Legit | 8 |
| Autoclicker | 6 |
| Reach | 6 |
| Killaura/triggerbot | 2 |

All of this is currently one player (me)

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