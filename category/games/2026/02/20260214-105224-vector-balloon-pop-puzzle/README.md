# Vector Balloon Pop Puzzle

Strategic physics-based puzzle where players pop colored balloons using limited darts to clear the grid.

## Description

A 10x10 grid is filled with balloons of 4 different colors. Players control a dart launcher at the bottom, aiming to clear all balloons with a limited number of darts. Hitting a balloon triggers a chain reaction - all adjacent balloons of the same color also pop. Balloons float upward to fill empty spaces after pops.

## Game Mechanics

- **Grid Size**: 10x10
- **Colors**: Red, Blue, Green, Yellow
- **Dart Limit**: 15 darts
- **Scoring**: Points = (Number of Popped Balloons)^2 * 10
- **Win Condition**: Clear all balloons
- **Lose Condition**: Run out of darts with balloons remaining

## How to Play

1. Move the launcher left/right using Arrow Keys
2. Aim the trajectory (automatic guide shows direction)
3. Press SPACE to fire a dart
4. Hit a balloon to trigger a pop
5. Same-colored neighbors also pop (chain reaction)
6. Score increases exponentially with chain reaction size
7. Clear the entire board to win

## Controls

| Key | Action |
|-----|--------|
| Left/Right Arrow | Move launcher |
| Space | Fire dart |
| R | Restart game |
| Escape | Quit |

## Build and Run

```bash
# Build
uv sync

# Run
uv run main.py
```

Or use the provided scripts:

```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Agent Observations

- `launcher_angle` - Current aim angle of the launcher
- `grid_state_matrix` - 10x10 matrix of balloon positions and colors
- `remaining_darts` - Number of darts left
- `current_score` - Current player score
