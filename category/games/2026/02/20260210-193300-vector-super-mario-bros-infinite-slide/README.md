# Vector Super Mario Bros - Infinite Slide

Master the physics of momentum in an endless icy platform sliding challenge.

## Description

An endless runner platformer with low-friction icy physics. Navigate across procedurally generated platforms while managing your momentum carefully. The screen scrolls from left to right, gradually increasing in speed. Balance the need to move forward with the risk of sliding off platforms due to high momentum.

## Rationale

This game focuses on friction and momentum mechanics, providing a unique challenge for both human players and RL agents to manage velocity and timing on slippery surfaces. It fills a niche not covered by standard platformers in the existing catalog.

## Details

- **Physics**: Low friction (0.05) creates slippery ice surfaces
- **Momentum**: Acceleration is gradual (0.2) but deceleration is very slow
- **Scroll**: Screen speed increases from 0.5 to 4.0 over time
- **Obstacles**: Spikes on platforms and gaps between platforms
- **Scoring**: +1 point per meter traveled, +50 per coin collected

### Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Apply force (accelerate in direction) |
| SPACE | Jump / Start |
| R | Restart (on game over) |
| ESC | Exit |

### Scoring

- Distance traveled: 1 point per meter
- Coins collected: 50 points each

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

## Stop

Press ESC or close the window. Or use:

```bash
pkill -f vector-super-mario-bros-infinite-slide
```

## How to Play

1. Press SPACE to start
2. Use LEFT/RIGHT arrows to apply force (not direct movement - it's slippery!)
3. Press SPACE to jump over gaps and spikes
4. Collect coins for bonus points
5. Stay ahead of the red scroll line on the left
6. Game ends if you fall, hit a spike, or get pushed off screen

## AI Agent Input

### Observation Space

```
Dict:
- player: {x, y, vx, vy}
- on_ground: bool
- nearest_platform: {x, y, width}
- nearest_coin: {x, y}
- scroll_x: float
- scroll_speed: float
```

### Action Space

```
Discrete(4):
- 0: No action
- 1: Move left
- 2: Move right
- 3: Jump
```

### Reward Structure

- Distance progress: +0.1 per frame
- Coin collected: +50
- Falling/dying: -100
- Survival bonus: +1 per frame

## Project Structure

```
category/games/2026/02/20260210-193300-vector-super-mario-bros-infinite-slide/
├── main.py           # Entry point
├── game.py           # Game loop and rendering
├── entities.py       # Player, Platform, Spike, Coin, LevelGenerator, GameState
├── config.py         # Constants and physics settings
├── appinfo.json      # App metadata
├── pyproject.toml    # Dependencies
└── README.md         # This file
```

## Technical Specs

- **Language**: Python 3.12+
- **Library**: pygame-ce 2.5+
- **Resolution**: 800x400
- **FPS**: 60
- **Physics**: Custom momentum-based with low friction

## Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```
