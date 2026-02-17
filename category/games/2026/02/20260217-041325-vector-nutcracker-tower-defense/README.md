# Vector Nutcracker Tower Defense

Protect the holiday toy box from a relentless march of wind-up mice in this minimalist tower defense strategy.

## Description

Place Nutcracker units on a 16x16 grid to defend the toy box from waves of wind-up mice. Enemies enter from the left and follow a pre-defined path. Choose between three tower types with different abilities to create strategic defenses.

## Rationale

Tower defense games provide an excellent environment for AI agents to learn strategic resource management, spatial positioning, and priority-based decision making. This simplified version focuses on clean vector graphics and core mechanics to reduce computational overhead during training.

## Game Mechanics

- **Grid**: 16x16 grid with a pre-defined enemy path
- **Enemies**: Wind-up mice enter from the left and march toward the toy box
- **Tower Types**:
  - **Scout** ($20): Fast fire rate, low damage, medium range
  - **Heavy** ($50): Slow fire rate, high damage, long range
  - **Frost** ($40): Slow fire rate, low damage, slows enemy movement
- **Health**: Lose health when enemies reach the toy box; game over at 0
- **Currency**: Earn gold by defeating enemies; spend on towers
- **Waves**: 10 progressively difficult waves

## Build

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

Or use the provided scripts:

Windows:
```bash
run.bat
```

Linux/Mac:
```bash
bash run.sh
```

## Stop

Press ESC during gameplay or close the game window.

## How to Play

1. Select a tower type with keys `1`, `2`, or `3`
2. Left-click on valid grid tiles (not on the path) to place towers
3. Towers automatically target and fire at enemies in range
4. Earn gold by defeating enemies
5. Survive all 10 waves to win

**Controls:**
- `1` - Select Scout Tower ($20)
- `2` - Select Heavy Tower ($50)
- `3` - Select Frost Tower ($40)
- `R` - Toggle tower range display
- `ESC` - Exit game
- `SPACE` - Restart (when game over)

## Scoring

- Enemy kill: Earn gold equal to enemy reward
- Wave completion: +100 points × wave number
- Score increases based on enemies defeated and time survived

## AI Agent Input

For RL agent control:
- Grid coordinates `(x, y)` for tower placement
- Tower type ID (1, 2, or 3) for tower selection

## Reward Structure

- Enemy kill: +reward value (15-40 depending on enemy type)
- Enemy reaches toy box: -50 equivalent (1 health lost)
- Wave completion bonus: +100 × wave number
- Efficiency measured by gold spent vs enemies killed

## Project Structure

```
category/games/2026/02/20260217-041325-vector-nutcracker-tower-defense/
├── main.py          - Entry point
├── game.py          - Main game loop and logic
├── config.py        - Game constants and settings
├── tower.py         - Tower and projectile classes
├── enemy.py         - Enemy class
├── pyproject.toml   - Dependencies
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
