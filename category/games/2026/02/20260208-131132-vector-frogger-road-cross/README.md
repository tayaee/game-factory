# Vector Frogger Road Cross

Navigate a busy highway and a rushing river to reach safety in this classic arcade reimagining.

## Description

A simplified Frogger clone where you control a frog starting at the bottom of the screen. The goal is to reach one of five lilypad slots at the top while avoiding moving vehicles on the road and staying afloat on logs in the water.

## Rationale

This project provides a perfect environment for Reinforcement Learning agents to master timing, obstacle avoidance, and pathfinding in a dynamic, multi-lane environment. It targets developers and AI researchers looking for a standardized benchmark for real-time spatial decision-making.

## Details

The game area consists of two main zones:
- **Road Zone**: 4 lanes with moving vehicles (cars and trucks) that must be avoided
- **Water Zone**: 5 lanes with floating logs that must be jumped on to stay afloat

Touching water or being hit by a vehicle results in immediate loss of a life. Levels progress by increasing the speed of all obstacles. The game state is represented by a grid-based coordinate system for easy processing by AI agents.

## Build

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## Stop

Press `ESC` or close the window.

## How to Play

Use Arrow Keys to move the frog one grid square at a time:
- **UP/DOWN/LEFT/RIGHT** - Move frog

**Scoring:**
- +10 points per lane moved forward
- +100 points for reaching a lilypad
- +500 bonus for completing a level (all 5 lilypads)
- -100 penalty for losing a life

**Goal:** Fill all 5 lilypads to complete a level. Speed increases each level.

## AI Agent Input

For RL agent control:

**Observation Space:**
- 12x16 grid (rows x cols) with categorical encoding:
  - 0: Empty/grass
  - 1: Road
  - 2: Water
  - 3: Car (moving left)
  - 4: Car (moving right)
  - 5: Truck (moving left)
  - 6: Truck (moving right)
  - 7: Log (moving left)
  - 8: Log (moving right)
  - 9: Lilypad (empty)
  - 10: Lilypad (filled)
  - 11: Frog position

**Action Space:**
- Discrete: [UP, DOWN, LEFT, RIGHT, NOOP]

**Reward Structure:**
- +10 per forward move
- +100 for reaching a lilypad
- -100 for death (collision or drowning)
- -0.1 per step (encourage efficiency)
- +500 for level completion

## Project Structure

```
category/games/2026/02/20260208-131132-000-vector-frogger-road-cross/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Game objects (Frog, Obstacle, Lane, Lilypad)
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 640x480
- **Frame Rate**: 30 FPS
- **Grid Size**: 40px (16 cols x 12 rows)
- **Input Type**: Discrete (Arrow keys)
