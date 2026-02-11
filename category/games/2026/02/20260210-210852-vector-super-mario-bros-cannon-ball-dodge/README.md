# Vector Super Mario Bros Cannon Ball Dodge

Dodge high-speed cannonballs while staying on moving platforms in this classic timing challenge.

## Description

The game consists of a single screen with three horizontal platforms. A cannon (Bill Blaster) is positioned on either the left or right edge of the screen at varying heights. The player controls a character that can move left, right, and jump. Every 2-3 seconds, a cannonball (Bullet Bill) is fired horizontally across the screen. The player must jump over or move between platforms to avoid contact.

## Game Rules

- **Scoring**: 10 points for every cannonball successfully avoided (when it leaves the screen)
- **Game Over**: Collision with any part of a cannonball or falling off the bottom of the screen
- **Physics**: Gravity is constant. Jump height is fixed. Cannonballs move at a linear velocity

## Controls

- **LEFT/RIGHT Arrow Keys**: Move horizontally
- **SPACE**: Jump
- **R**: Restart after game over
- **ESC**: Quit

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Unix/Linux/Mac: `./run.sh`

## Technical Specs

- **Language**: Python 3.10+
- **Framework**: Pygame
- **Resolution**: 800x600
- **Dependencies**: pygame

## AI Agent Info

**Observation Space**: Player X/Y, Player Velocity, Cannonball X/Y/Velocity list, Platform positions

**Action Space**:
- 0: Stay
- 1: Left
- 2: Right
- 3: Jump

**Reward Structure**:
- Positive reward (+0.1) for every frame alive
- Large positive (+10) for projectile pass
- Large negative (-100) for collision
