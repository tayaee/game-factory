# Vector Super Mario Bros Paratroopa Stomp

Master the art of mid-air precision by stomping on flying Koopa Paratroopas to stay aloft.

## Description

A vertical survival game where you must bounce on flying Paratroopas to stay in the air. Missing a stomp means falling to the ground, which resets your combo. Missing entirely and falling off the bottom of the screen ends the game.

## Rationale

This app targets AI agents interested in aerial trajectory prediction and sequential jumping logic. The game focuses on verticality and timing, serving as a specialized training ground for reinforcement learning agents to learn mid-air precision and momentum management.

## Details

### Physics System

- **Gravity**: 0.5 acceleration with 15.0 terminal velocity
- **Jump Impulse**: -10.0 for initial ground jump
- **Bounce Impulse**: -12.0 when stomping an enemy (higher than regular jump)

### Paratroopa Behavior

- **Spawn Rate**: New enemy every 1.5 seconds
- **Movement Pattern**: Sinusoidal vertical motion with horizontal drift
- **Speed Range**: 2.0 to 5.0 pixels per frame
- **Bounce**: Enemies bounce off screen edges
- **Descent**: Paratroopas gradually descend over time

### Scoring

- **Base Points**: 100 points per stomp
- **Combo Multiplier**: Doubles for each consecutive stomp without touching ground
  - 1 stomp: x1 (100 points)
  - 2 stomps: x2 (200 points)
  - 3 stomps: x4 (400 points)
  - 4 stomps: x8 (800 points)
- **Combo Reset**: Touching the ground or missing a stomp resets combo

### Hazards

- **Side/Bottom Collision**: Hitting the side or bottom of a Paratroopa is instant death
- **Falling Off Screen**: Falling past the bottom edge ends the game

## Build

```bash
uv sync
```

## Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## Stop

Press ESC or close the window.

## How to Play

### Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Move horizontally |
| SPACE | Jump (from ground) |
| ESC | Exit game |
| SPACE (when game over) | Restart |

### Goal

Survive as long as possible by stomping Paratroopas to stay airborne. Build combos by chaining stomps without touching the ground for higher scores.

### Tips

- Time your jumps to land on the top of Paratroopas
- Build horizontal momentum to reach enemies at the edges
- Higher combo multipliers yield exponentially more points
- The game gets harder over time with more enemies spawning

## Project Structure

```
category/games/2026/02/20260211-154530-vector-super-mario-bros-paratroopa-stomp/
├── main.py           # Entry point
├── game.py           # Game loop and rendering
├── entities.py       # Player, Paratroopa classes
├── config.py         # Constants and settings
├── pyproject.toml    # Dependencies
├── run.bat           # Windows run script
├── run.sh            # Unix run script
└── README.md         # This file
```

## AI Agent Input

### Observation Space

```python
{
    'player': {
        'x': float,           # Normalized position (0-1)
        'y': float,
        'vx': float,          # Normalized velocity
        'vy': float,
        'on_ground': bool,
        'has_jumped': bool
    },
    'nearest_paratroopa': {
        'x': float,
        'y': float,
        'distance': float,    # Normalized distance
        'direction': int      # 1 or -1
    } or None,
    'paratroopa_count': int,
    'combo': int,
    'score': int
}
```

### Action Space

Discrete actions:
- 0: No action
- 1: Move left
- 2: Move right
- 3: Jump
- 4: Jump + Move left
- 5: Jump + Move right

### Reward Structure

- Successful stomp: +100 * (2 ^ combo)
- Combo maintained: Additional reward per frame in air
- Death: -1000 (game over)

## Technical Specs

- **Language**: Python 3.12+
- **Library**: pygame-ce 2.5+
- **Resolution**: 800x600
- **FPS**: 60
- **Style**: Vector/minimal aesthetic
