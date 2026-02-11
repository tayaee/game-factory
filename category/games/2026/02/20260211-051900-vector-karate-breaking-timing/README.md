# Vector Karate Breaking - Timing Game

Master the art of focus and timing to break solid wood, stone, and ice blocks.

## Description

This game focuses on high-precision timing and reaction speed, a core mechanic found in classic arcade bonus stages like Street Fighter. It serves as an excellent environment for Reinforcement Learning agents to learn optimal action timing relative to a moving gauge.

## Game Mechanics

- **Gauge Speed**: Increases as the level progresses
- **Target Zone**: A specific range (e.g., 90-100) on the 0-100 scale
- **Lives**: 3 attempts allowed per block type
- **Progression**: Successful breaks lead to harder materials and faster moving bars

## Materials

| Material | Color | Threshold | Zone Width |
|----------|-------|-----------|------------|
| Thin Wood | Brown | 85 | 15 |
| Thick Wood | Dark Brown | 88 | 12 |
| Stone | Gray | 90 | 10 |
| Ice | Light Blue | 92 | 8 |
| Diamond | Pale Blue | 95 | 6 |

## Technical Specs

- **Framework**: Pygame
- **Resolution**: 800x600
- **State Space**: Current gauge position, target zone bounds, material type, speed
- **Action Space**: Discrete(1) - [0: Idle, 1: Strike]

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Start

Windows:
```batch
run.bat
```

Linux/Mac:
```bash
chmod +x run.sh
./run.sh
```

Or directly:
```bash
uv run --no-active --python 3.12 main.py
```

Note: Python 3.12 is required. Pygame is not compatible with Python 3.14.

## How to Play

1. Watch the moving gauge on the right side of the screen
2. Press the **SPACE** key when the slider is inside the red target zone at the top
3. Breaking a block grants 100 points plus a bonus based on how close you were to the maximum value (100)
4. If you miss the zone, the block remains intact and you lose one life

## Controls

| Key | Action |
|-----|--------|
| SPACE | Strike / Continue |
| R | Restart (when game over) |
| ESC | Quit game |

## How to Stop

Press ESC or close the window.

## How to Cleanup

```bash
rm -rf .venv
```
