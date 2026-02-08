# Vector Snake Grid Survival

Navigate the grid and grow longer without hitting walls or your own tail in this minimalist arcade classic.

## Description

A classic Snake game implementation on a 20x20 grid where the player controls a continuously moving snake. The objective is to eat food to grow longer while avoiding collisions with walls and the snake's own body. The game features a clean vector aesthetic with increasing difficulty as the snake grows.

## Rationale

Snake is a fundamental benchmark for reinforcement learning and logic-based AI agents. It provides a clear objective with simple state-space transitions, making it ideal for testing pathfinding algorithms, spatial awareness, and decision-making under constraints. The game's straightforward rules and win/lose conditions create an excellent environment for AI experimentation.

## Details

The game consists of a 20x20 grid where a snake moves continuously in a cardinal direction. The snake starts at length 3 in the center of the grid. A single food item spawns at a random empty coordinate. When the snake eats food, its length increases by 1, the score increases by 10, and a new food item spawns. The frame rate increases slightly as the snake grows to add progressive difficulty. The game ends if the snake's head hits the grid boundary or any part of its own body.

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

Use Arrow Keys or WASD to control the snake's direction:
- **UP/W** - Move up
- **DOWN/S** - Move down
- **LEFT/A** - Move left
- **RIGHT/D** - Move right

You cannot reverse direction directly (e.g., cannot go Down if moving Up).

**Scoring:**
- +10 points per food eaten
- Speed increases with each food consumed

**Goal:** Eat as much food as possible without colliding with walls or yourself.

## AI Agent Input

For RL agent control:

**State Space:**
- Grid coordinates (x, y): 20x20 = 400 possible positions
- Snake body positions: List of coordinate tuples
- Food position: (x, y) coordinate
- Current direction: 0 (up), 1 (down), 2 (left), 3 (right)

**Action Space:**
- 0: Up
- 1: Down
- 2: Left
- 3: Right

**Reward Structure:**
- Food consumption: +10
- Each step survived: +0 (can be modified to +0.1 for alternative training)
- Collision/Game Over: -100

**Observation Format:**
The game state can be represented as:
- 20x20 grid with categorical encoding (0: empty, 1: snake body, 2: snake head, 3: food)
- Or as raw coordinates: [head_x, head_y, food_x, food_y, direction]

## Project Structure

```
category/games/2026/02/20260208-172500-vector-snake-grid-survival/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Snake and Food classes
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 640x680
- **Frame Rate**: 15 FPS (starts at 8 FPS, increases to 20 FPS)
- **Grid Size**: 32px (20 cols x 20 rows)
- **Input Type**: Discrete (Arrow keys, WASD)
- **Game Engine**: Pygame 2.0+
