# Vector Snow Bros - Platform Clear

Turn enemies into snowballs and roll them to clear the floor in this classic arcade platformer.

## Description

A single-screen platformer where you control a character that shoots snow breath. Enemies hit by snow breath gradually freeze. Once fully frozen, the enemy becomes a snowball. Push the snowball to roll it along platforms, fall down ledges, and bounce off walls, destroying any non-frozen enemies in its path.

## Technical Details

- **Engine**: Pygame
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Physics**: Rigid body collision for snowballs, grid-based patrolling for enemies

## How to Build

```bash
uv init && uv add pygame
```

Or with Python 3.11 (recommended for pygame compatibility):
```bash
uv venv --python 3.11 && uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

Or directly with Python:
```bash
python main.py
```

## How to Stop

Press `ESC` or close the window. For CLI termination, use `Ctrl+C`.

## How to Play

- **Arrow Keys**: Move left/right
- **Space**: Jump
- **Z**: Shoot snow breath / Push snowball
- **R**: Restart (after game over or level clear)
- **ESC**: Quit

**Scoring**:
- Freeze an enemy: +100 points
- Snowball kill: +500 points
- Clear a level: +1000 points

Avoid contact with unfrozen enemies to prevent life loss. You have 3 lives.

## How to Cleanup

```bash
rm -rf .venv && rm pyproject.toml uv.lock
```
