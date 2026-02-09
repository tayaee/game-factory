# Vector Ice Hockey Classic

A fast-paced 1v1 ice hockey duel featuring physics-based puck movement and strategic positioning.

## Description

Play against an AI opponent in a top-down ice hockey match. Control your player with the arrow keys, collide with the puck to shoot it, and try to score more goals than your opponent within 3 minutes.

## Rationale

Ice hockey offers a unique challenge for AI agents due to the frictionless movement (sliding) and the need to predict puck trajectories. This simplified version focuses on core mechanics, making it an ideal environment for testing competitive multi-agent reinforcement learning or simple reflex-based logic.

## Details

The game is played on a rectangular rink with:
- **Player Half**: Bottom portion of the rink (red player)
- **Opponent Half**: Top portion of the rink (blue AI)
- **Goals**: Located at the center of each end wall
- **Center Line**: Divides the rink into two halves

Physics features:
- Puck slides with minimal friction
- Players transfer velocity to the puck on impact
- Puck bounces off walls (except when entering goal area)
- 3-minute timed matches

The AI opponent tracks the puck and moves to defend its goal while attempting to score on yours.

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

## Stop

Press `ESC` or close the window.

## How to Play

Use Arrow Keys to move your player:
- **UP/DOWN/LEFT/RIGHT** - Move player (diagonal movement supported)

**Gameplay:**
- Hit the puck into the opponent's goal (top) to score
- Defend your goal (bottom) from the AI
- Higher velocity hits result in faster puck movement
- The puck bounces off walls
- Match lasts 3 minutes

**Scoring:**
- +1 point for each goal scored
- Most goals when time expires wins

## AI Agent Input

For RL agent control:

**Observation Space:**
- Puck position (x, y)
- Puck velocity (vx, vy)
- Player position (x, y)
- Opponent position (x, y)
- Goal positions
- Time remaining

**Action Space:**
- Discrete(9): [None, Up, Down, Left, Right, Up-Left, Up-Right, Down-Left, Down-Right]

**Reward Structure:**
- +100 for scoring a goal
- -100 for conceding a goal
- -0.1 per step (encourage efficiency)
- +1 for hitting the puck toward opponent's goal

## Project Structure

```
category/games/2026/02/20260209-045050-vector-ice-hockey-classic/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Game objects (Puck, Player, AIOpponent)
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Input Type**: Continuous (Arrow keys)
- **Language**: Python 3.12+
- **Library**: pygame-ce
