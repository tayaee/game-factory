# Vector Tetris Grid Logic

Clear horizontal lines using strategically falling geometric blocks in this timeless puzzle classic.

## Description

A faithful Tetris implementation featuring a 10x20 grid with all seven classic Tetromino shapes (I, O, T, S, Z, J, L). The game includes ghost piece preview, hold functionality, wall kick rotation system, and progressive difficulty scaling. Pieces are randomized using the 7-bag system for fair distribution.

## Rationale

Tetris is the quintessential spatial optimization game, perfect for AI research in reinforcement learning and pattern recognition. The constrained grid environment with falling pieces provides an excellent testbed for agents learning long-term planning, risk assessment, and spatial reasoning. The scoring system rewards efficiency (line clears) while penalizing poor placement decisions.

## Details

The game consists of a 10x20 grid where seven different Tetrominoes fall from the top one at a time. Each piece is composed of four square blocks. The goal is to rotate and move pieces to create solid horizontal lines without gaps. When a line is completed, it disappears and blocks above fall down. The game ends if pieces stack up to the top of the grid.

**Key Features:**
- Ghost piece showing landing position
- Hold piece functionality (once per drop)
- Wall kick rotation system for smooth gameplay
- 7-bag randomizer ensures fair piece distribution
- Progressive speed increase every 10 lines
- Lock delay prevents accidental drops

**Scoring:**
- 1 line: 100 points
- 2 lines: 300 points
- 3 lines: 500 points
- 4 lines (Tetris): 800 points
- Soft drop: 1 point per cell
- Hard drop: 2 points per cell

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

**Controls:**
- **Left/Right Arrow** - Move piece left/right
- **Down Arrow** - Soft drop (faster fall)
- **Up Arrow / X** - Rotate clockwise
- **Z** - Rotate counter-clockwise
- **Space** - Hard drop (instant placement)
- **C / Left Shift** - Hold piece
- **P** - Pause game
- **R** - Restart game
- **ESC** - Quit

**Strategy:**
- Create flat surfaces to avoid creating holes
- Plan for T-Spins and Tetrises (4-line clears)
- Use hold piece strategically for difficult shapes
- Keep the right side clear for I-piece placement
- Higher levels increase fall speed significantly

## AI Agent Input

For RL agent control:

**State Space:**
- 2D grid array (10x20): 0 for empty, 1-7 for block types
- Current piece type and rotation
- Next piece type
- Hold piece status

**Action Space:**
- Discrete(6): Left, Right, Down, Rotate CW, Hard Drop, Hold

**Reward Structure:**
- Line clear: +100 to +800 (based on lines)
- Hard drop: +2 per cell
- Soft drop: +1 per cell
- Invalid move: -0.1

**Termination:**
- Game over when pieces reach the top

## Project Structure

```
category/games/2026/02/20260208-175000-vector-tetris-grid-logic/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── entities.py      - GameState and Tetromino classes
├── config.py        - Game constants, colors, shapes
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 500x650
- **Grid Size**: 10x20 (28px blocks)
- **Frame Rate**: 60 FPS
- **Initial Fall Speed**: 800ms per row
- **Min Fall Speed**: 100ms
- **Speed Increase**: Every 10 lines cleared
- **Lock Delay**: 500ms
- **Game Engine**: Pygame 2.0+
