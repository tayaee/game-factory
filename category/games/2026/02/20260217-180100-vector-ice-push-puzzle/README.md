# Vector Ice Push Puzzle

Slide ice blocks strategically to reach the goal and solve the frozen maze.

## Description

A strategic sliding puzzle game where you navigate through a frozen 10x10 grid maze. When you press a direction, both your character and any pushable ice blocks slide until they hit a wall or another block. Plan your moves carefully to create pathways and reach the golden goal circle.

## Controls

- **Arrow Keys**: Move and slide in any direction
- **R**: Restart game
- **ESC**: Quit

## Gameplay

- **Sliding Mechanics**: Movement is continuous until you hit an obstacle
- **Ice Blocks**: Push blue ice blocks to create stopping points or clear paths
- **Goal**: Navigate to the golden circle to complete each level
- **Scoring**: Higher scores for fewer moves (1000 - moves * 10)

## Game Features

- 5 progressively challenging levels
- Vector-style minimalist graphics
- Strategic block pushing mechanics
- Cumulative scoring across all levels

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py

# Or use the provided scripts:
# Windows: run.bat
# Linux/Mac: run.sh
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Grid Size**: 10x10
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **State Space**: Player position, ice block positions, goal position, grid layout
- **AI Training**: Suitable for reinforcement learning agents testing pathfinding, state-space navigation, and multi-step planning

## Reward Function (AI Training)

- Goal reach: +100.0
- Each move: -1.0
- Level completion bonus: +1000.0 / moves_taken

## Game Rules

- Player and ice blocks slide continuously in the chosen direction until hitting a wall, another ice block, or the grid boundary
- Pushing an ice block requires space beyond it
- The level is complete when the player reaches the goal position
- No game over condition - puzzle solving only
