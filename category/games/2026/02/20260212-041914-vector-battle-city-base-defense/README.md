# Vector Battle City Base Defense

Defend your base from incoming enemy tanks in this top-down strategic shooter.

## Description

A simplified 2D top-down tank combat game inspired by the classic Battle City. The player controls a gold tank on a 13x13 grid battlefield. The objective is to destroy all 10 enemy tanks while preventing them from reaching or destroying your base (the eagle icon) located at the bottom center.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC key or close the window.

## How to Play

- **Arrow Keys**: Move tank (Up, Down, Left, Right)
- **SPACE**: Fire bullets
- **SPACE**: Start game from menu
- **R**: Restart after game over
- **ESC**: Quit

### Gameplay Tips

1. Protect your base at all costs - one hit destroys it!
2. Brick walls can be destroyed to create paths
3. Steel walls are indestructible - use them as cover
4. Water blocks tank movement but bullets fly over it
5. Destroy all 10 enemy tanks to win
6. You have 3 lives - use them wisely

### Enemy Types

- **Red (Normal)**: Standard speed and firepower - 100 points
- **Orange (Fast)**: Moves 1.5x faster - 200 points
- **Purple (Power)**: Faster bullets - 300 points
- **Blue (Armor)**: Takes multiple hits - 400 points

### Map Elements

- **Brick Wall**: Destructible, provides temporary cover
- **Steel Wall**: Indestructible, permanent cover
- **Water**: Impassable for tanks, bullets fly over

## Technical Details

- **Language**: Python 3.12+
- **Framework**: Pygame
- **Resolution**: 520x580
- **Dependencies**: Managed via uv

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
category/games/2026/02/20260212-041914-vector-battle-city-base-defense/
├── main.py           # Entry point
├── game.py           # Main game logic
├── entities.py       # Tank, Bullet, Grid, Base classes
├── config.py         # Constants and configuration
├── pyproject.toml    # Dependencies
├── appinfo.json      # Metadata
├── run.bat           # Windows run script
├── run.sh            # Linux/Mac run script
└── README.md         # This file
```
