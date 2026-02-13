# Vector Frogger: Logs and Turtles

Cross the treacherous river by hopping on floating logs and diving turtles in this timing-based classic.

## Description

A focused river-crossing challenge where you control a frog starting at the bottom of the screen. The goal is to reach the goal area at the top while jumping on floating logs and turtles that move at different speeds and directions. Logs are stable platforms, but turtles periodically submerge - if you're on a turtle when it submerges, you fall into the water.

## Rationale

This game focuses on the river-crossing mechanic of Frogger, providing a high-stakes environment for AI agents to learn predictive movement and timing. It targets developers interested in grid-based pathfinding and collision detection in dynamic environments.

## Details

The game area consists of:
- **Start Zone**: Bottom row (row 9) - safe starting position
- **River Zone**: Rows 1-8 with floating logs and turtles moving horizontally at different speeds and directions
- **Goal Zone**: Top row (row 0) - reaching this area grants points and resets position

Each successful crossing increases your score. Every 3 crossings increases the level, making platforms move faster. If you touch the water (miss a platform), stand on a submerged turtle, or ride a platform off-screen, you lose a life.

**Turtle Submersion**: Turtles cycle between visible and submerged states every 3 seconds. Submerged turtles appear dark blue and cannot support the frog - standing on one when it submerges causes death.

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## Stop

Press `ESC` or close the window.

## How to Play

Use Arrow Keys to move the frog one grid square at a time:
- **UP/DOWN/LEFT/RIGHT** - Move frog

**Scoring:**
- +10 points each time you move forward to a new row
- +100 points for reaching the goal area
- Level increases every 3 successful crossings (platform speed increases)
- -50 penalty for losing a life
- -1 per frame (time pressure)

**Goal:** Reach the goal area as many times as possible. Game ends when all 3 lives are lost.

**Important:** Jump off turtles before they turn dark blue (submerged) - you cannot stand on submerged turtles!

## AI Agent Input

For RL agent control:

**Observation Space:**
- 10x10 grid with categorical encoding:
  - 0: Empty/grass/safe zone
  - 1: Water
  - 2: Log (moving right)
  - 3: Log (moving left)
  - 4: Turtle (visible)
  - 5: Turtle (submerged)
  - 6: Frog position
  - 7: Goal area

**Action Space:**
- Discrete: [UP, DOWN, LEFT, RIGHT]

**Reward Structure:**
- +10 for moving forward to a new row
- +100 for reaching goal
- -50 for death (water, submerged turtle, or off-screen)
- -1 per frame (encourage efficiency)

## Project Structure

```
category/games/2026/02/20260213-030212-vector-frogger-logs-and-turtles/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Game objects (Frog, Log, Turtle, Lane)
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
├── appinfo.json     - App metadata
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 600x600
- **Frame Rate**: 60 FPS
- **Grid Size**: 60px (10 cols x 10 rows)
- **Input Type**: Discrete (Arrow keys)
- **Language**: Python 3.12+
- **Library**: pygame-ce
- **Turtle Cycle**: 3 seconds visible, 1 second submerged
