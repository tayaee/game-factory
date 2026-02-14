# Vector Snake Rattle Coin Dash

Navigate the isometric grid, collect golden coins, and avoid your growing tail in this classic logic puzzle.

## Description

A 2.5D isometric take on the classic Snake game. The player controls a continuously moving snake on a diamond-shaped isometric grid. The objective is to collect randomly spawning golden coins to grow longer and increase score while avoiding collisions with grid boundaries and the snake's own body. The game features a minimalist black-and-white aesthetic with gold accents, increasing speed difficulty, and smooth isometric graphics.

## Rationale

This game targets fans of classic arcade logic and spatial reasoning challenges. The isometric perspective adds a unique visual dimension to the familiar Snake mechanics, making it ideal for testing AI pathfinding algorithms and reinforcement learning agents in a spatially complex but rule-constrained environment. The 2.5D view requires agents to process diagonal visual information while maintaining logical grid-based movement.

## Details

The game features a 20x20 isometric diamond grid rendered in a 2.5D perspective. The snake starts at length 3 in the center of the grid, moving continuously in one of four cardinal directions relative to the isometric grid. A single golden coin spawns at a random empty grid coordinate. When the snake's head collects a coin, the snake grows by 1 segment, score increases by 100 points, and a new coin spawns at a different random location. Every 5 coins collected increases the game speed progressively. The game ends if the snake's head collides with the grid boundary or any part of its own body. The visual style uses high-contrast monochromatic vector graphics (white on black) with golden coins for a professional minimalist aesthetic.

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

Use Arrow Keys or WASD to control the snake's direction on the isometric diamond grid:
- **UP/W** - Move north (up-left on screen)
- **DOWN/S** - Move south (down-right on screen)
- **LEFT/A** - Move west (down-left on screen)
- **RIGHT/D** - Move east (up-right on screen)

You cannot reverse direction directly (e.g., cannot go South if moving North).

**Scoring:**
- +100 points per coin collected
- Speed increases every 5 coins collected
- Game Over: -100 penalty

**Goal:** Collect as many golden coins as possible without colliding with grid boundaries or your own body.

## AI Agent Input

For RL agent control:

**State Space:**
- Snake head position (x, y): 20x20 = 400 possible positions
- Coin position (x, y): 20x20 = 400 possible positions
- Snake body segments: List of up to 400 coordinate tuples
- Current direction: 0 (north), 1 (south), 2 (west), 3 (east)
- Relative distances to walls in each direction

**Action Space:**
- 0: Move North (up-left on isometric grid)
- 1: Move South (down-right on isometric grid)
- 2: Move West (down-left on isometric grid)
- 3: Move East (up-right on isometric grid)

**Reward Structure:**
- Coin collected: +10
- Collision/Game Over: -100
- Step penalty: -0.1 (optional, for training efficiency)

**Observation Format:**
The game state can be represented as:
- 20x20 isometric grid with categorical encoding (0: empty, 1: snake body, 2: snake head, 3: coin)
- Or as raw coordinates: [head_x, head_y, coin_x, coin_y, direction, body_segments...]

## Project Structure

```
category/games/2026/02/20260214-062200-vector-snake-rattle-coin-dash/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Snake and Coin classes with isometric rendering
├── config.py        - Game constants and isometric conversion functions
├── pyproject.toml   - Dependencies
├── appinfo.json     - App metadata
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x600
- **Frame Rate**: 15 FPS (starts at 8 FPS, increases to 20 FPS)
- **Grid Size**: 20x20 isometric diamond grid
- **Input Type**: Discrete (Arrow keys, WASD)
- **Game Engine**: Pygame 2.0+
- **Color Palette**: Black (#000000), White (#FFFFFF), Gold (#FFD700)
