# Vector Super Mario Bros: Turtle Shell Kick

Master the chain reaction by kicking turtle shells to clear waves of enemies.

## Description

A single-screen survival/score-attack game focusing on projectile physics and chain reactions. The player controls a character on a flat platform where enemies (Koopas) spawn from both sides. Jump on a Koopa to turn it into a stationary shell, then kick the shell to send it flying across the screen. Hitting multiple enemies with a single shell kick exponentially increases your score.

## Technical Specs

- **Engine**: Pygame
- **Resolution**: 800x400
- **FPS**: 60
- **Input**: Keyboard (Arrow keys + Space)

## Game Rules

| Action | Effect |
|--------|--------|
| Stomp enemy | Transforms Koopa into a stationary Shell |
| Kick shell | Touching a stationary shell moves it in the direction of impact |
| Chain reaction | Moving shell kills Koopas. Consecutive kills increase points (100, 200, 400, 800...) |
| Game over | Collision with walking Koopa or moving Shell |

## How to Build

```bash
uv run python -m pip install pygame
```

## How to Start

```bash
uv run main.py
```

## How to Play

- **LEFT/RIGHT**: Move
- **SPACE**: Jump
- Jump on a Koopa to turn it into a shell
- Walk into the shell to kick it
- Hit multiple enemies with one shell for exponential score multipliers
- Avoid touching walking enemies or shells already in motion

## How to Stop

Press ESC or close the window.

## How to Cleanup

```bash
rm -rf .venv
```
