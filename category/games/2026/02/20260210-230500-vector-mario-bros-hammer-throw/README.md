# Vector Mario Bros: Hammer Throw

Master the trajectory to knock down koopas with precision hammer tosses.

## Description

This game focuses on projectile physics and timing, inspired by the classic Hammer Bro mechanics. It provides a specialized environment for RL agents to learn parabolic trajectories, velocity estimation, and lead-target shooting in a 2D space.

The player controls a character fixed on a platform. Enemies (Koopas and Goombas) move across different levels. The player's primary action is tossing hammers. The hammer follows a parabolic path influenced by an initial velocity vector (angle and power). The game ends if an enemy touches the player or if the player runs out of hammers.

## State Space

- `player_pos`: x, y coordinates
- `enemy_list`: list of {x, y, type, velocity}
- `hammer_count`: integer
- `active_hammers`: list of {x, y, vx, vy}

## Action Space

- `throw`: boolean
- `angle`: float (10 to 80 degrees)
- `power`: float (100 to 500)

## Reward Structure

- `enemy_hit`: +10 points
- `multi_kill`: +25 points
- `missed_throw`: -1 point
- `game_over`: -50 points

## Game Mechanics

- `gravity`: 500.0 pixels/s²
- `character_position`: [100, 450]
- `enemy_spawn_rate`: Every 3 seconds
- `hitbox_type`: Circular for hammers, Rectangular for enemies
- `levels`: 3 platform heights

## Controls

- **UP / DOWN** - Adjust throw angle
- **SPACE (hold)** - Charge power
- **SPACE (release)** - Throw hammer
- **R** - Restart (when game over)
- **ESC** - Exit game

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press **ESC** or close the window.

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specifications

- Resolution: 800x600
- FPS: 60
- Language: Python 3.12+
- Library: pygame-ce

## Project Structure

```
vector-mario-bros-hammer-throw/
├── main.py       # Entry point
├── game.py       # Main game loop and rendering
├── entities.py   # Game entities (Player, Hammer, Enemy, Platform)
├── config.py     # Configuration constants
├── pyproject.toml
├── appinfo.json  # Metadata
├── run.bat       # Windows run script
├── run.sh        # Linux/Mac run script
└── README.md
```
