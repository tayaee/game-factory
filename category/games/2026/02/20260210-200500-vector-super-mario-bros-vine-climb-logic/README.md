# Vector Super Mario Bros Vine Climb Logic

Master the rhythmic vertical ascent by climbing hidden vines while avoiding aerial hazards.

## Description

This app focuses on vertical movement mechanics and timing-based obstacle avoidance. It targets developers interested in ladder/climbing physics and provides a focused environment for reinforcement learning agents to learn vertical spatial navigation and rhythmic input patterns.

## Details

The game simulates the classic hidden vine climbing mechanic. The player controls a character on a vertical vine. The screen scrolls upward automatically as the player climbs. Obstacles like Koopa Paratroopas or Lakitu's Spiny eggs move horizontally across the screen. The player must move up, down, or switch sides of the vine to avoid contact.

Physics constants:
- Climb Speed = 3.0
- Side Switch Speed = 4.0
- Gravity = 0.3
- Auto-scroll Speed = 0.5

The game includes a stamina meter that depletes if the player stays still for too long, encouraging constant upward progress. Difficulty increases with altitude as obstacles spawn more frequently.

## Technical Specs

- Engine: Pygame
- Resolution: 400x600
- FPS: 60

### State Space
- player_y: Vertical position
- player_vel_y: Vertical velocity
- player_side: Which side of vine (-1 left, 1 right)
- stamina: Current stamina level
- altitude: Total height climbed

### Action Space (Discrete 5)
- NOOP: No action (drains stamina)
- UP: Climb upward
- DOWN: Climb downward
- LEFT: Switch to left side of vine
- RIGHT: Switch to right side of vine

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press ESC or close the window.

## How to Play

- UP/DOWN arrow keys to climb the vine
- LEFT/RIGHT arrow keys to shift to the left or right side of the vine to dodge enemies
- Collect coins placed along the vine for bonus points (+10 each)
- Score increases based on the altitude reached
- Game ends if the player touches an enemy or the stamina meter reaches zero
- Keep moving to maintain stamina

## Reward Function

- +0.1 per unit of upward movement
- +10 per coin collected
- -0.01 penalty for staying still
- -100 on collision (game over)

## Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```
