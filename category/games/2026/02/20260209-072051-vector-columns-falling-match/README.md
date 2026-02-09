# Vector Columns Falling Match

Align three or more matching gems in vertical, horizontal, or diagonal lines as they fall.

## Description

A faithful recreation of the classic Columns puzzle game featuring a 6x13 vertical grid. Triplets of gems fall from the top, and players can shift them left/right and cycle the gem order within the column. When three or more gems of the same color align in any direction, they disappear, and gems above fall down, potentially creating chain reactions.

## Rationale

Columns is the quintessential pattern-matching puzzle game, perfect for AI research in reinforcement learning and spatial reasoning. The constrained grid environment with falling triplets provides an excellent testbed for agents learning pattern anticipation, strategic planning, and understanding chain reactions through gravity-based mechanics.

## Details

The game consists of a 6x13 vertical grid where triplets of gems (columns) fall continuously. Each triplet contains three gems that may be of different or identical colors, randomly generated from six available types. The player controls the horizontal position and can cycle the vertical order of gems within the falling column.

When a column lands and locks into place, the game scans for three or more adjacent gems of the same color in vertical, horizontal, or diagonal directions. All matching gems are cleared simultaneously, and any gems above the cleared spaces fall down to fill the voids. This can create new matches, resulting in chain reactions with multiplied scoring.

The game ends when gems stack up to the top of the grid, blocking new columns from spawning.

**Key Features:**
- 6x13 grid with six gem types
- Cycle gem order within the falling column
- Match detection in all 8 directions
- Chain reaction system with score multipliers
- Progressive difficulty (speed increases)
- Lock delay for precise placement

**Scoring:**
- Base: 100 points per gem cleared
- Chain multiplier: 1.5x per chain level
- Higher chains yield exponentially more points

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
- **Left/Right Arrow** - Move column left/right
- **Up Arrow** - Cycle gem order within column (top becomes middle, middle becomes bottom, bottom becomes top)
- **Down Arrow** - Soft drop (faster fall)
- **Space** - Hard drop (instant placement)
- **P** - Pause game
- **R** - Restart game
- **ESC** - Quit

**Strategy:**
- Plan ahead by looking at the current and next positions
- Use the cycle ability to create matches as the column falls
- Set up chain reactions by clearing gems that will cause above gems to form new matches
- Keep the grid lower to avoid game over
- Higher levels increase fall speed significantly

## AI Agent Input

For RL agent control:

**State Space:**
- 2D grid array (6x13): 0 for empty, 1-6 for gem colors
- Current falling triplet colors and position
- Current score and game status

**Action Space:**
- Discrete(5): No op, Left, Right, Cycle, Hard drop

**Reward Structure:**
- Gems cleared: +100 * count * (1.5 ^ (chain_level - 1))
- Game over: -1000 (terminal)

**Termination:**
- Game over when grid fills to the top

## Project Structure

```
category/games/2026/02/20260209-072051-vector-columns-falling-match/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── entities.py      - GameState and FallingColumn classes
├── config.py        - Game constants, colors, settings
├── pyproject.toml   - Dependencies
├── appinfo.json     - Metadata
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 500x650
- **Grid Size**: 6x13 (40px cells)
- **Frame Rate**: 60 FPS
- **Initial Fall Speed**: 800ms per row
- **Min Fall Speed**: 100ms
- **Lock Delay**: 300ms
- **Gem Types**: 6 colors
- **Game Engine**: Pygame-ce 2.5+
