# Vector Pental Line Connector

A strategic logic puzzle where you connect five stones to dominate the board.

## Description

This game targets fans of classic abstract strategy like Gomoku or Connect Four. It provides a perfect environment for AI agents to learn spatial reasoning, pattern recognition, and minimax-based decision-making with a clear win/loss reward system.

## Details

The game is a simplified version of Gomoku played on a 15x15 grid. Players take turns placing a black or white stone on an empty intersection. The objective is to be the first to form an unbroken line of exactly five stones horizontally, vertically, or diagonally. The game engine handles turn-based logic, illegal move prevention (e.g., placing on an occupied spot), and win-state detection. For AI training, the board state is exported as a 2D array where 0 is empty, 1 is Player 1, and 2 is Player 2.

## Technical Stack

- Python 3.12+
- Package manager: uv
- Graphics library: pygame-ce
- Configuration: pyproject.toml

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

```bash
pkill -f main.py
```

## How to Play

Players use the mouse left-click to place a stone on grid intersections. To increase the score, the agent must complete a line of 5 stones. Points are awarded +100 for a win, -100 for a loss, and +1 for each sequence of 3 or 4 stones created during the process. The game ends when one player connects five or the board is full (draw).

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## AI Integration

- **Observation Space**: 15x15 integer matrix representing the grid state
- **Action Space**: Integer from 0 to 224 representing the chosen cell index on the 15x15 grid

Access board state via `game.get_board_matrix()` and action space size via `game.get_action_space_size()`.
