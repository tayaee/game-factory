# Vector Pengo: Ice Block Sniping

Calculate trajectories and slide ice blocks to eliminate moving targets in this precision puzzle action game.

## Category
Games

## Description
The game is set on a 2D grid representing an icy arena. The player controls a character who can push ice blocks located in the environment. Unlike standard sokoban or basic push games, the objective here is to 'snipe' enemies by sliding blocks across the grid.

## Rules
1. Ice blocks slide until they hit a wall, another block, or an enemy
2. Enemies move in predictable patterns (back and forth or circular)
3. Eliminating an enemy requires timing the slide so the block occupies the same grid cell as the enemy during movement
4. Multiple enemies can be crushed with a single slide for combo points
5. If an enemy touches the player, the game ends
6. Levels are cleared when all enemies are eliminated

## How to Build
```bash
uv run python -m venv .venv && source .venv/bin/activate && uv pip install pygame
```

## How to Start
```bash
uv run main.py
# Or use the provided scripts:
# Windows: run.bat
# Linux/Mac: ./run.sh
```

## How to Stop
Press ESC or close the window. For agents, send SIGINT.

## How to Play
Use ARROW KEYS to move the character. When adjacent to an ice block, move toward it to push it in that direction. Your goal is to slide these blocks into moving enemies. Scores increase based on the number of enemies destroyed and the speed of level completion.

## How to Cleanup
```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Specs

### Engine
Pygame

### State Space
Grid matrix (16 x 16) containing player pos, block positions, and enemy trajectories.

### Action Space
Discrete: [0: Up, 1: Down, 2: Left, 3: Right, 4: Wait]

### Reward Structure
- +100 for hitting enemy
- +500 for level clear
- -1 per step to encourage efficiency
- -1000 for death

## Project Structure
```
category/games/2026/02/20260218-075050-vector-pengo-ice-block-sniping/
├── main.py
├── run.bat
├── run.sh
└── README.md
```

## Screenshots
UI consists of a 16x16 grid with blue blocks, red enemy circles, and a green player square.
