# Vector Super Mario Bros - Springboard Physics

Master the timing of physics-based spring jumps to reach high-altitude platforms.

## Description

This game focuses on the specific mechanic of variable jump heights using a springboard, a classic element in platformers. It provides a specialized environment for AI agents to learn momentum conservation and timing-dependent velocity multipliers, which are core to advanced platforming logic.

The game features a single-screen environment with a character (Mario-like) and several springboards (jump pads) scattered on the floor. Platforms are positioned at varying heights, some unreachable by normal jumping. The primary mechanic is the springboard logic: if the player lands on a spring and presses the jump key at the exact moment of compression, they receive a 2.5x vertical velocity boost. If they don't press jump, they receive a standard 1.2x bounce.

## Requirements

- Python >= 3.10
- pygame-ce

## Game Rules

| Parameter | Value |
|-----------|-------|
| Gravity | 0.8 |
| Normal Jump Velocity | -12 |
| Spring Boost Multiplier | 2.5x |
| Passive Bounce Multiplier | 1.2x |
| Win Condition | Collect all coins (10 coins total) |
| Lose Condition | Falling below the screen boundary |

## Technical Specifications

- **Resolution**: 800x600
- **FPS**: 60
- **Input Type**: Keyboard

### State Representation

| Variable | Description |
|----------|-------------|
| player_x | Player X position |
| player_y | Player Y position |
| player_vx | Player horizontal velocity |
| player_vy | Player vertical velocity |
| nearest_spring_dist | Distance to nearest springboard |
| spring_compression_state | Spring compression state |

## How to Build

```bash
uv run python -m pip install pygame-ce
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press `ESC` key or close the window.

## How to Play

1. Move left and right using **Arrow Keys** (or A/D)
2. Press **Space** to jump (or W/Up Arrow)
3. To perform a high jump:
   - Land on a red springboard
   - Press **Space** exactly when the spring is compressed
4. Score increases by **100 points** for each coin collected
5. Reaching the highest platform grants a **500-point bonus**

### Controls

| Key | Action |
|-----|--------|
| Left Arrow / A | Move Left |
| Right Arrow / D | Move Right |
| Space / W / Up Arrow | Jump |
| R | Restart Game |
| ESC | Quit |

## How to Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```

## Project Structure

```
.
├── main.py
├── README.md
├── run.bat
└── run.sh
```

## Gameplay Tips

1. Use passive bounces (1.2x) for low platforms
2. Time your jumps perfectly for boosted springs (2.5x) to reach high platforms
3. The compression window is approximately 8 frames - practice makes perfect
4. Collect all 10 coins to win
5. Reach the top platform for a 500-point bonus
