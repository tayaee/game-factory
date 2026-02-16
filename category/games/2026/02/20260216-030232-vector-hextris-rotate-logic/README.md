# Vector Hextris - Rotate Logic

A fast-paced hexagonal puzzle game where you match colored bars by rotating a central hexagon.

## Description

The game features a large hexagon in the center of the screen that the player can rotate left or right. Colored bars fall from the six outer edges of the screen towards the center. The goal is to stack these bars on the sides of the hexagon. When three or more bars of the same color touch, they are cleared, and the player earns points. If the bars stack outside the boundary of the hexagonal play area, the game ends.

## How to Build

```bash
uv venv
uv pip install pygame
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

- Use `LEFT` arrow key to rotate the hexagon counter-clockwise
- Use `RIGHT` arrow key to rotate the hexagon clockwise
- Match 3 or more blocks of the same color on any side to clear them
- Score is based on blocks cleared and current speed multiplier
- Game over occurs when any stack reaches the outer limit line

## Controls

| Key | Action |
|-----|--------|
| Left Arrow | Rotate counter-clockwise |
| Right Arrow | Rotate clockwise |
| R | Restart (when game over) |
| Q | Quit (when game over) |
| ESC | Quit anytime |

## Scoring

- Base score: 10 points per block cleared
- Speed multiplier: Higher speed = more points
- Combo bonus: Clearing larger groups at once increases score

## Technical Details

- **Language**: Python 3.12+
- **Framework**: Pygame
- **Resolution**: 800x600
- **FPS**: 60

## How to Cleanup

```bash
rm -rf .venv
```

## Project Structure

```
.
├── main.py          # Entry point
├── game.py          # Game logic and rendering
├── entities.py      # Hexagon, Block, and FallingBar classes
├── config.py        # Game constants and settings
├── pyproject.toml   # Project dependencies
├── appinfo.json     # App metadata
├── README.md        # This file
├── run.bat          # Windows launcher
└── run.sh           # Linux/Mac launcher
```
