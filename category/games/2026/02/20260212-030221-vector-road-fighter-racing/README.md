# Vector Road Fighter Racing

Navigate high-speed highways, dodge traffic, and reach the finish line before running out of fuel.

## Description

A simplified clone of the classic Road Fighter arcade game. The player controls a car on a vertically scrolling 4-lane highway. The goal is to reach a specific distance (10,000 units) while avoiding collisions with other vehicles. Crashing causes speed loss and fuel depletion. Fuel tanks appear periodically and must be collected to prevent running out of fuel.

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

- **LEFT / RIGHT arrow keys**: Change lanes
- **UP arrow key**: Accelerate
- **DOWN arrow key**: Brake
- **SPACE**: Start game from menu
- **R**: Restart after game over
- **ESC**: Quit

### Gameplay Tips

1. Avoid other cars - collisions slow you down and consume fuel
2. Collect fuel canisters marked with 'F' to replenish your fuel gauge
3. Higher speed covers more distance but consumes fuel faster
4. Orange erratic cars change lanes randomly - be extra careful!
5. Reach 10,000 distance units to win

## Technical Details

- **Language**: Python 3.12+
- **Framework**: Pygame
- **Resolution**: 400x600
- **Dependencies**: Managed via uv

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
category/games/2026/02/20260212-030221-vector-road-fighter-racing/
├── main.py           # Entry point
├── game.py           # Main game logic
├── entities.py       # Player, Enemy, FuelTank classes
├── config.py         # Constants and configuration
├── pyproject.toml    # Dependencies
├── appinfo.json      # Metadata
├── run.bat           # Windows run script
├── run.sh            # Linux/Mac run script
└── README.md         # This file
```
