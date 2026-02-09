# Vector Heian-Kyo Alien Trap

Strategic pitfall trapping game inspired by the 1980 classic Heian-kyo Alien.

## Description

A reimagining of the classic arcade game where players must trap aliens by digging holes in the floor. The game combines spatial reasoning with timing mechanics - aliens wander the maze with simple AI, and the player must create pitfalls, lure aliens into them, and bury them before they escape.

## Rationale

This game focuses on spatial management and timing rather than fast reflexes alone. It targets players who enjoy classic arcade strategy and provides a clear environment for reinforcement learning agents to learn pathfinding and predictive movement.

## Details

The player controls a character in a grid-based maze. Aliens roam the maze randomly or with simple pursuit logic. The player must dig a hole in the floor, wait for an alien to fall into it, and then fill the hole to eliminate the alien.

**Key Mechanics:**
1. Move freely through the maze avoiding aliens
2. Press Z to dig a hole at your current location (takes time)
3. Lure aliens into the holes by strategic positioning
4. Stand adjacent to a hole and press X to fill it, burying any trapped alien
5. If an alien stays in a hole too long without being buried, it escapes
6. Clear all aliens to advance to the next level

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

**Controls:**
- **Arrow Keys / WASD** - Move the player
- **Z** - Dig a hole at current position
- **X** - Fill adjacent hole (bury trapped alien)
- **R** - Restart current level
- **ESC** - Quit

**Scoring:**
- +100 points for trapping an alien in a hole
- +500 points for burying an alien
- Lose 1 life if an alien touches you
- Start with 3 lives

**Strategy:**
- Dig holes in corridors where aliens are likely to pass
- Aliens have a timer while trapped - bury them quickly before they escape
- Higher levels have more aliens and more complex wall layouts
- Plan escape routes when digging near multiple aliens

## AI Agent Input

For RL agent control:

**State Space:**
- 2D grid array (15 rows x 20 cols) with values:
  - 0: Empty floor
  - 1: Wall
  - 2: Hole
  - 3: Player
  - 4: Alien
  - 5: Hole with trapped alien

**Action Space:**
- Discrete(6): Up, Down, Left, Right, Dig, Fill

**Reward Structure:**
- Step penalty: -0.01
- Trap alien: +1.0
- Bury alien: +5.0
- Death penalty: -10.0
- Win bonus: +20.0

## Project Structure

```
category/games/2026/02/20260209-074052-vector-heian-kyo-alien-trap/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── entities.py      - GameState and Alien classes
├── config.py        - Game constants, colors, and settings
├── pyproject.toml   - Dependencies
├── appinfo.json     - App metadata
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 1000x750
- **Grid Size**: 20x15 tiles (48px each)
- **Frame Rate**: 60 FPS
- **Game Engine**: Pygame 2.0+
- **Levels**: Progressive difficulty with more aliens and walls
