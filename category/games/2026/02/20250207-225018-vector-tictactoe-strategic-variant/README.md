# Vector Tic-Tac-Toe: Strategic Variant

Strategic tic-tac-toe variant with limited pieces and movement mechanics for deeper gameplay.

## Description

A twist on classic tic-tac-toe where each player has only 3 pieces. After placing all pieces, you must move existing pieces to adjacent cells to win. The movement restriction creates a strategic puzzle that rewards planning over speed.

## Rationale

Traditional tic-tac-toe often ends in draws due to its solved nature. By limiting pieces to 3 per player and requiring movement after placement, the game becomes a dynamic strategy puzzle. This creates an excellent environment for reinforcement learning with a manageable state space and clear strategic decisions.

## Game Mechanics

- **Board**: 3x3 grid
- **Pieces**: Each player has 3 pieces (Blue for Player 1, Red for Player 2)
- **Placement Phase**: First 3 turns, place pieces on empty cells
- **Movement Phase**: After all 6 pieces are placed, move your pieces to adjacent empty cells (including diagonals)
- **Win Condition**: First to get 3 in a row (horizontal, vertical, or diagonal)
- **Draw Condition**: Same board state repeats 3 times

## Tech Stack

- Python 3.10+
- Pygame
- uv (package manager)

## Build

```bash
uv venv
uv pip install pygame
```

## Run

```bash
uv run main.py
```

## Stop

Close the game window or press ESC.

## How to Play

1. Player 1 (Blue) goes first
2. Click empty cells to place your pieces (3 per player)
3. After all pieces are placed, click one of your pieces to select it
4. Click an adjacent empty cell (including diagonals) to move
5. First to align 3 pieces in a row wins

**Controls:**
- `Left Click` - Place piece / Select piece / Move piece
- `ESC` - Quit game
- `SPACE` - Restart (when game over)

## AI Agent Integration

**State Space:**
- 9 cells with values: 0 (empty), 1 (Player 1), 2 (Player 2)
- Board state represented as 9-digit string for repetition detection

**Action Space:**
- Placement phase: Select cell index (0-8)
- Movement phase: Select piece, then select destination (from position, to position)

**Reward Structure:**
- Win: +100
- Loss: -100
- Draw: 0
- Per turn: +1 (for current player)

**Valid Actions:**
- The `get_valid_moves(player)` method returns all legal moves as `[(from_pos, to_pos), ...]`
- For placement: `(None, (row, col))`
- For movement: `((from_row, from_col), (to_row, to_col))`

## Project Structure

```
category/games/2026/02/1738965018-vector-tictactoe-strategic-variant/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── board.py         - Board logic, move validation, win detection
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
```
