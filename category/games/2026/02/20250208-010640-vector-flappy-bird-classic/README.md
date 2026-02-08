# Vector Flappy Bird Classic

**Category:** Games

**Description:** Navigate a minimalist bird through moving pipes in this physics-based vertical scroller.

## Rationale

Flappy Bird is a staple of simple yet addictive game mechanics. This version provides a clean, vector-based environment ideal for training reinforcement learning agents to master precise timing and collision avoidance.

## Details

The game features a bird controlled by gravity and a jump action. Obstacles consist of vertical pipes with gaps that move from right to left. The bird must pass through the gaps without touching the pipes or the ground. Physics include a constant downward acceleration (gravity) and a fixed upward velocity burst on each jump. The game ends immediately upon collision.

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

- **Spacebar** / **Mouse Left Click**: Jump
- **Escape**: Quit the game

## Features

- Physics-based gravity and jumping mechanics
- Procedurally generated pipe positions
- Score tracking with high score persistence
- Clean vector graphics style
- AI-friendly observation interface for reinforcement learning

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including bird position, velocity, and pipe information
- `step_ai(action)`: Execute an action (0: do nothing, 1: jump) and receive (observation, reward, done)

### Reward Structure

- Per frame alive: +0.1
- Pipe cleared: +1.0
- Collision: -10.0

### Observation Space

```python
{
    "bird_y": float,              # Bird Y position
    "bird_velocity": float,        # Bird Y velocity
    "next_pipe_dist_x": float,    # Distance to next pipe
    "next_pipe_gap_y": float,     # Top of gap Y position
    "next_pipe_gap_bottom": float,# Bottom of gap Y position
    "score": int,
    "game_state": str
}
```

### Action Space

- 0: Do nothing (fall)
- 1: Jump

## How to Stop

Press ESC key or close the game window. For automation, send SIGINT (Ctrl+C).

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame
- **Resolution:** 800x600
- **Input:** Keyboard / Mouse click / Action space (for AI)
