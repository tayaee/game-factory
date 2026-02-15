# Vector Diamond Mine Puzzle Classic

Grid-based puzzle game where you navigate a mine to collect diamonds while avoiding falling boulders.

## Overview

**Category:** games

**Description:** Navigate a grid-based mine to collect diamonds while avoiding falling boulders. Exit opens when all diamonds are collected.

**Target Audience:** Puzzle game enthusiasts, AI/ML researchers (excellent for reinforcement learning with spatial reasoning and long-term planning)

## How It Works

- 20x15 grid with walls, dirt, diamonds, boulders, and an exit
- Player moves through dirt (which disappears) and collects diamonds
- Boulders fall when the space below them becomes empty
- Boulders can be pushed left or right if there's space
- Exit door opens when all diamonds are collected
- Standing under a falling boulder causes death

## Project Structure

```
20260215-023800-vector-diamond-mine-puzzle-classic/
├── main.py         # Game implementation with DiamondMineGame class
├── run.bat         # Windows launch script
├── run.sh          # Linux/Mac launch script
└── README.md       # This file
```

## How to Build

```bash
uv add --python 3.12 pygame
```

## How to Start

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or directly:**
```bash
uv run --no-active --python 3.12 main.py
```

## How to Play

**Controls:**
- Arrow Keys or WASD: Move player
- R: Restart after game over
- ESC: Quit game

**Scoring:**
- Collect diamond: +50 points
- Reach exit: +500 points
- Each step: -1 point
- Death: -1000 points

**Tips:**
- Collect all diamonds to open the exit (purple door turns green)
- Don't stand directly under boulders when digging dirt below them
- Boulders can be pushed left or right
- Boulders roll off other boulders to the side

## How to Stop

Press ESC or close the game window.

## How to Cleanup

```bash
# Remove virtual environment
rm -rf .venv

# Remove uv cache
uv cache clean
```

## AI/ML Integration

The game is designed for AI training:

- **State Space:** 20x15 grid, 4 discrete actions
- **Observation Methods:** `get_state()` (dict), `get_grid_state()` (2D array)
- **Reward Structure:** +50 (diamond), +500 (exit), -1 (step), -1000 (death)
- **Headless Mode:** Initialize with `DiamondMineGame(render=False)` for training

Example AI usage:
```python
from main import DiamondMineGame, Action

game = DiamondMineGame(render=False)
game.reset()

while not game.game_over:
    action = your_ai_model.get_action(game.get_grid_state())
    reward, done, score = game.step(action)
```
