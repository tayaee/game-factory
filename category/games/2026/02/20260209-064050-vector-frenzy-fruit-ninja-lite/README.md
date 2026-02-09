# Vector Frenzy: Fruit Ninja Lite

Slice falling fruits with precision swipes while avoiding dangerous bombs in this vector-style reflex challenge.

## Description

A simplified 2D physics-based slicing game. Various circular "fruits" are tossed into the screen from the bottom at different angles and velocities. The player must move a cursor or swipe to intersect these objects. If a fruit is sliced, it splits into two halves and adds points. Occasionally, "bombs" are tossed; hitting a bomb results in an immediate game over or point deduction. The game speeds up as time progresses, increasing the frequency of spawns.

## Game Rules

| Rule | Value |
|------|-------|
| Fruit Score | +10 points |
| Bomb Penalty | Game Over |
| Miss Penalty | -5 points, lose 1 life |
| Win Condition | Survival and high score accumulation |
| Physics | Gravity-affected projectiles with parabolic arcs |

## How to Build

```bash
uv init
uv add pygame
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

Move the mouse cursor rapidly across the falling circles (fruits) to slice them. Each slice increases your score. Do not touch the red spiked circles (bombs). If a fruit falls off the bottom of the screen without being sliced, you lose health or points. High scores are recorded based on the number of successful consecutive slices.

## How to Cleanup

```bash
rm -rf .venv && rm pyproject.toml uv.lock
```
