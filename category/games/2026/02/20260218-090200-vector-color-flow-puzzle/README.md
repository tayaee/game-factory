# Vector Color Flow Puzzle

**Category:** Games

**Description:** Connect matching colors with pipes to fill the entire grid and create a perfect flow.

## Rationale

This game targets puzzle enthusiasts who enjoy spatial reasoning and logic. It offers a clean, minimalist aesthetic that focuses on pure problem-solving without distractions. For AI agents, it provides a deterministic environment to practice pathfinding and constraint satisfaction algorithms.

## Details

The game consists of an NxN grid with pairs of colored dots placed in various cells. The objective is to draw lines (pipes) connecting dots of the same color.

Rules:
1. Every pair of dots must be connected
2. Pipes cannot cross each other
3. Every single cell in the grid must be occupied by a pipe
4. Pipes can only move horizontally and vertically

The game starts with a 5x5 grid and increases in complexity. The UI is rendered using a single-color background (dark grey) with high-contrast solid colors for the pipes and dots.

## How to Build

```bash
uv venv
uv pip install pygame
```

Or simply run:
```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Unix: `run.sh`

## Controls

- **Mouse Click and Drag**: Draw pipes connecting same-colored dots
- **R**: Reset the current level
- **Space**: Advance to next level (after completion)
- **Escape**: Quit the game

## How to Play

Goal: Fill 100% of the grid by connecting all color pairs.

Scoring:
- Each completed connection adds 100 points
- Completing the board gives a bonus based on time remaining

Controls: Click and drag from one colored dot to its match. Pipes can only move horizontally and vertically. Use 'R' to reset the current level.

Pathfinding agents should minimize the length of pipes while ensuring no cells remain empty.

## Features

- Progressive difficulty with increasing number of color pairs
- Time limit for each level with bonus for fast completion
- Clean vector graphics with high-contrast colors
- AI-friendly observation interface for reinforcement learning
- Score tracking with high score persistence

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including grid configuration and dot positions
- `get_valid_actions()`: Returns list of valid actions for the current state

### Observation Space

```python
{
    "grid": List[List[int]],     # NxN matrix with color IDs (0 = empty)
    "grid_size": int,            # Grid dimension
    "num_colors": int,           # Number of color pairs
    "level_time": float,         # Remaining time in seconds
    "score": int,                # Current score
    "game_state": str,           # "playing", "level_complete", "game_over"
    "dot_positions": List[Tuple] # List of (r1, c1, r2, c2) for each color pair
}
```

### Action Space

Actions are encoded as integers:
- For each color (1 to num_colors), actions 0-3 represent:
  - 0: Move Up
  - 1: Move Down
  - 2: Move Left
  - 3: Move Right

### Reward Structure

- Completed color connection: +100
- Level completion: +time_bonus (time_remaining * 10)
- Game over: 0

## How to Stop

Press ESC key or close the game window. For CLI termination, use Ctrl+C.

## How to Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** Pygame 2.5.0+
- **Grid Logic:** Matrix-based path validation
- **Dependency Management:** uv
- **Resolution:** 800x800
- **FPS:** 60
