# Vector Tower Defense Lite

Simple geometric tower defense game where strategic tower placement stops waves of enemies.

## Description

Place geometric towers along a winding path to defend your base from incoming enemy waves. Choose between two tower types with different range, damage, and cost characteristics.

## Rationale

Tower defense games provide an optimal environment for reinforcement learning agents to learn resource allocation and positional strategy, while remaining intuitive for all players.

## Game Mechanics

- **Map**: Single winding path from start to end point
- **Enemies (Creeps)**: Spawn at intervals from the start point, moving along the path to the end
- **Towers**: Place towers on empty ground adjacent to the path; they automatically attack enemies in range
- **Resources**: Earn gold by defeating enemies; spend it to build new towers
- **Lives**: Lose a life when an enemy reaches the end; game over at 0 lives

## Tech Stack

- Python 3.10+
- Pygame
- uv (package manager)

## Build

```bash
uv venv
uv pip install pygame
```

## Run

```bash
uv run main.py
```

## Stop

Close the game window or press Ctrl+C.

## How to Play

1. Select tower type with number keys (1=Basic, 2=Sniper)
2. Click on valid ground (not on path) to place towers
3. Towers automatically attack enemies in range
4. Earn gold from kills to build more towers
5. Survive as many waves as possible

**Controls:**
- `1` - Select Basic Tower ($50, medium range/damage)
- `2` - Select Sniper Tower ($100, long range/high damage)
- `R` - Toggle tower range display
- `SPACE` - Restart (when game over)

## AI Agent Input

For RL agent control:
- Coordinates `(x, y)` for tower placement
- Tower type ID (1 or 2) for tower selection

## Reward Structure

- Enemy kill: +10 points
- Base damage (life lost): -50 equivalent
- Gold bonus per wave cleared
- Efficiency measured by gold spent vs enemies killed

## Project Structure

```
category/games/2026/02/1738964309-vector-tower-defense-lite/
├── main.py          - Entry point
├── game.py          - Main game loop and logic
├── config.py        - Game constants and settings
├── path.py          - Enemy path definition
├── tower.py         - Tower and projectile classes
├── enemy.py         - Enemy class
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Cleanup

```bash
rm -rf .venv
find . -type d -name "__pycache__" -exec rm -rf {} +
```
