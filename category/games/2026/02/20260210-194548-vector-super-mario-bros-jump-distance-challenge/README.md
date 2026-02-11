# Vector Super Mario Bros Jump Distance Challenge

Master the art of momentum and timing to clear increasingly wide gaps in this Mario-inspired physics challenge.

## Description

This app focuses on the core platforming mechanic of Super Mario Bros: the variable jump. It is designed for reinforcement learning agents to learn the relationship between horizontal velocity (running) and vertical impulse (jumping) to clear gaps that require precise input duration.

## Details

The game features a simplified 2D side-scrolling environment. The player controls a character standing on a platform. To the right is a pit of varying width and a landing platform. The goal is to cross as many pits as possible. The width of the pit increases with each successful jump.

Physics constants:
- Gravity = 0.8
- Max Run Speed = 6.0
- Jump Impulse = 12.0

The game ends if the character falls into the pit.

## Technical Specs

- Engine: Pygame
- Resolution: 800x400
- FPS: 60

### State Space
- player_x_velocity
- player_y_velocity
- distance_to_pit
- pit_width
- is_grounded

### Action Space
- NOOP
- MOVE_RIGHT
- JUMP
- MOVE_RIGHT_AND_JUMP

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Close the pygame window or press Ctrl+C in the terminal.

## How to Play

- RIGHT ARROW key to gain momentum
- SPACE BAR to jump (press and hold for higher jumps)
- Score increases by 1 for every pit successfully crossed
- Score is weighted by the width of the pit cleared
- Falling into a pit resets the game

## Reward Function

Positive reward for distance traveled while in the air and a large bonus for landing on the far platform. Negative reward for falling into the pit.

## Cleanup

```bash
rm -rf .venv
```
