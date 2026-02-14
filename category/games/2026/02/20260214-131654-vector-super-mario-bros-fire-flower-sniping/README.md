# Vector Super Mario Bros Fire Flower Sniping

Master the trajectory of Mario's fireballs to defeat enemies in a high-stakes sniping challenge.

## Description

A physics-based projectile game where you control Mario to defeat waves of enemies using bouncing fireballs. Fireballs follow realistic trajectory physics with gravity and coefficient of restitution, bouncing off floors, walls, and platforms. Strategic aiming and positioning are required to hit all enemies before running out of ammunition.

## Game Mechanics

- **Screen Resolution**: 800x600
- **FPS**: 60
- **Fireball Gravity**: 0.5
- **Bounce Velocity Multiplier**: 0.8
- **Starting Lives**: 3
- **Fireball Limit Per Stage**: 15
- **Enemy Collision Score**: 100
- **Multi-Hit Bonus**: 2.0x (after bounces)
- **Stage Clear Bonus**: 500

## How to Play

1. Aim Mario's arm up and down using UP/DOWN Arrow keys to change the launch angle
2. Press SPACE to shoot a fireball
3. Use LEFT/RIGHT Arrow keys to move Mario slightly to adjust the bounce starting point
4. Fireballs bounce off floors, walls, and platforms according to physics
5. Each fireball has a limited number of bounces before disappearing
6. Score increases by hitting enemies - direct hits grant standard points, hits after multiple bounces grant bonus multipliers
7. Clear all enemies to advance to the next stage
8. Game ends if ammunition runs out before all enemies are cleared or if enemies reach Mario's position

## Controls

| Key | Action |
|-----|--------|
| Up/Down Arrow | Adjust aim angle |
| Left/Right Arrow | Move Mario |
| Space | Shoot fireball |
| R | Restart game |
| Escape | Quit |

## Build and Run

```bash
# Build
uv sync

# Run
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:

```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

## Cleanup

```bash
rm -rf .venv
```

## Agent Observations

- `player_x` - Mario's horizontal position
- `arm_angle` - Current aim angle in radians
- `fireballs_remaining` - Number of fireballs left for current stage
- `fireballs[]` - List of active fireballs with positions and velocities
- `enemies[]` - List of remaining enemies with positions and types
- `platforms[]` - List of platform positions and dimensions
- `current_score` - Current player score
- `current_stage` - Current stage number
