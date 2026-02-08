# Vector Pinball Gravity Physics

**Category:** Games

**Description:** A high-stakes minimalist pinball simulation with realistic physics and score multipliers.

## Rationale

Pinball offers a perfect environment for AI agents to learn predictive physics and timing-based decision making. It targets casual players looking for classic arcade thrills and developers interested in 2D collision dynamics.

## Details

The game consists of a 400x600 rectangular field. Key components include a metal ball (circle), two flippers (rotating lines/rectangles) at the bottom, and various circular bumpers and triangular slingshots. Gravity constantly pulls the ball down. The ball bounces off walls and objects based on reflection vectors. Scoring occurs when the ball hits bumpers. If the ball falls through the gap between flippers, the game ends. Physics should handle variable velocity and basic friction.

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Run

```bash
uv run main.py
```

## Controls

- **Left Arrow**: Activate left flipper
- **Right Arrow**: Activate right flipper
- **Space**: Start game / Restart after game over
- **Escape**: Quit the game

## How to Play

Score points by hitting bumpers. Each bumper hit increases the current score. Use the Left Arrow key to trigger the left flipper and the Right Arrow key for the right flipper. Flippers rotate upward rapidly when pressed and return to baseline when released. The goal is to keep the ball in play as long as possible while maximizing the score through combo hits.

## Features

- Realistic gravity and friction physics
- Rotating flipper mechanics with momentum transfer
- Circular bumpers with bounce physics
- Triangular slingshots for deflection
- Complex wall layout for varied ball paths
- Score tracking with high score persistence
- Clean vector graphics style
- AI-friendly observation interface for reinforcement learning

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including ball position, velocity, and flipper angles
- `step_ai(action)`: Execute an action and receive (observation, reward, done)

### Action Space

- 0: Idle (do nothing)
- 1: Left flipper up
- 2: Right flipper up
- 3: Both flippers up

### Observation Space

```python
{
    "ball_x": float,              # Ball X position
    "ball_y": float,              # Ball Y position
    "ball_vx": float,             # Ball X velocity
    "ball_vy": float,             # Ball Y velocity
    "left_flipper_angle": float,  # Normalized left flipper angle (0-1)
    "right_flipper_angle": float, # Normalized right flipper angle (0-1)
    "score": int,                 # Current score
    "ball_count": int,            # Remaining balls
    "game_state": str             # "ready", "playing", or "game_over"
}
```

### Reward Structure

- Bumper hit: +10
- Survival per frame: +0.1
- Ball lost: -100

## How to Stop

Press ESC key or close the game window. For automation, send SIGINT (Ctrl+C).

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame
- **Resolution:** 400x600
- **FPS:** 60
- **Gravity Constant:** 0.5
- **Restitution Coefficient:** 0.8
