# Vector Reversi Othello Logic

A strategic board game of territory and conversion where one move can flip the entire board.

## Description

Reversi (Othello) is a classic strategy game that provides a perfect environment for AI agents to learn tactical positioning, edge control, and long-term planning. Two players take turns placing pieces on an 8x8 grid, capturing opponent pieces by surrounding them in straight lines.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the platform-specific scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Press `ESC` or close the window, or use:
```bash
kill $(pgrep -f 'uv run main.py')
```

## How to Play

1. Use the mouse to click on a highlighted valid square to place your piece
2. Your goal is to surround the opponent's pieces to flip them to your color
3. Focus on capturing corners as they cannot be flipped back
4. The score increases as you convert more opponent pieces to your own
5. The game automatically skips a player's turn if they have no valid moves
6. Press `R` to restart the game

## Controls

- **Mouse**: Click on valid squares (green dots) to place your piece
- **R**: Restart game
- **ESC**: Quit

## Technical Specifications

| Property | Value |
|----------|-------|
| Grid Size | 8x8 |
| Winning Condition | Higher piece count at end-of-game |
| Input Method | Mouse click on valid grid coordinates |
| State Representation | 2D integer array (0: empty, 1: black, 2: white) |

## AI Agent Input

For AI/RL integration, the game state is represented as an 8x8 grid:
- `0`: Empty cell
- `1`: Black piece
- `2`: White piece

Valid moves are encoded as coordinates (row, col) where placing a piece would flip at least one opponent piece.

## How to Cleanup

```bash
rm -rf .venv
```
