# Vector Lode Runner Gold Collect

Navigate platforms and dig traps to collect all gold pieces while avoiding guards.

## Description

A simplified version of the classic Lode Runner. Navigate a 2D grid-based platformer where you must collect all gold pieces to reveal the exit ladder. Use strategic digging to trap pursuing guards and create safe paths. Features gravity physics, climbable ladders, and AI enemies that chase you through the level.

## Technical Specifications

- **Language**: Python 3.12+
- **Rendering**: pygame-ce
- **Environment**: 20x15 grid, 32px tiles (640x480 resolution)
- **Physics**: Gravity-based with ladders and temporary holes

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Start

```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# Or directly
uv run --no-active --python 3.12 python main.py
```

## How to Stop

Press ESC to quit, or close the window.

## How to Play

- **Arrow Keys** or **WASD**: Move and climb ladders
- **Z**: Dig hole to the left
- **X**: Dig hole to the right

### Scoring

| Action | Points |
|--------|--------|
| Collect gold | +50 |
| Trap enemy in hole | +20 |
| Complete level | +500 |
| Lose a life | -100 |

### Goal

Collect all gold pieces on each level to reveal the exit ladder at the top. Reach the exit to advance. You have 3 lives. Guards will chase you - use digging to trap them temporarily (4 seconds) and create safe paths. Holes regenerate after 5 seconds.

## Reward Structure (RL)

- Gold collection: +50
- Trapping enemy: +20
- Level complete: +500
- Game over: -100

## How to Cleanup

```bash
rm -rf .venv
find . -type d -name '__pycache__' -exec rm -rf {} +
```
