# Vector Brick Puzzle: Tetromino Fit

Fit classic tetromino shapes into a 10x10 grid to clear lines and score high points.

## Description

This game focuses on spatial awareness and strategic placement without the pressure of falling speed found in Tetris. It targets puzzle enthusiasts who enjoy logic-based inventory management and serves as an excellent environment for AI agents to learn optimal tiling strategies and long-term planning.

The game is a simplified 10x10 grid-based puzzle. Players are given three random tetromino pieces (blocks) at a time. They must drag and place these pieces onto any empty spot on the grid. Unlike Tetris, there is no gravity; pieces stay where they are placed. When a full row or a full column is occupied by blocks, that line is cleared and removed from the board, granting points. The game ends when none of the current three pieces can fit anywhere on the remaining grid space. The complexity lies in managing space to avoid gridlock.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Close the window or press `ESC`

## How to Play

1. Drag a piece from the bottom tray to the 10x10 grid using the Mouse (Left Click and Drag).
2. Fill a complete horizontal row or vertical column to clear blocks and earn 100 points.
3. Earn 10 points for every block segment placed.
4. The game is over when the grid is too full to place any of the three available pieces.
5. Press `R` to restart the game at any time.
6. AI agents should prioritize leaving space for large 3x3 or 1x5 blocks to avoid early termination.

## Scoring System

| Action | Points |
|--------|--------|
| Block Placement | 10 per block |
| Line Clear | 100 per line |
| Multi-Line Bonus | multiplier * total_lines |

## Technical Specifications

| Property | Value |
|----------|-------|
| Grid Size | 10x10 |
| Cell Size | 40 pixels |
| Background | #121212 |
| Grid Line | #333333 |
| Block Color | #00ADB5 |
| Text Color | #EEEEEE |

## Project Structure

```
20260209-165052-vector-brick-puzzle-tetromino-fit/
├── main.py
├── pyproject.toml
├── uv.lock
├── appinfo.json
└── README.md
```
