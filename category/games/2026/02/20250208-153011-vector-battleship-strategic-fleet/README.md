# Vector Battleship: Strategic Fleet

Classic tactical naval warfare game against a smart AI opponent.

## Description

A faithful implementation of the classic Battleship game with a probability-based AI opponent. Place your fleet strategically and hunt down enemy ships before they sink yours.

## Rationale

Battleship is a timeless strategic puzzle that requires logical deduction and probability estimation. This version provides a clean, vector-based interface for casual players and a structured environment for reinforcement learning agents to master search-and-destroy tactics.

## Details

The game is played on a 10x10 grid. Each player has a fleet of 5 ships: Carrier (5), Battleship (4), Destroyer (3), Submarine (3), and Patrol Boat (2). The game proceeds in rounds. In each round, the player chooses a coordinate to fire upon. If a ship occupies that coordinate, it is a hit; otherwise, it is a miss. A ship is sunk when all its squares are hit. The objective is to sink the entire enemy fleet before they sink yours. The UI uses monochromatic vector graphics for high visibility and clear game state representation.

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run python main.py
```

## How to Stop

Close the game window or press ESC.

## How to Play

Score increases for every successful hit (+10) and significantly for sinking a ship (+50). Use the mouse to click on the 10x10 enemy grid to select coordinates. In RL mode, agents send integer pairs (x, y) via stdin or API. The game ends when one side's total ship health (17 hits) reaches zero.

**Controls:**
- `Left Click` - Fire at enemy position
- `ESC` - Quit game
- `SPACE` - Restart (when game over)

## AI Training Data

**State Representation:**
100-length integer array: 0=unknown, 1=miss, 2=hit, 3=sunk

**Reward Structure:**
- Hit: +10
- Miss: -1
- Sink: +50
- Win: +200
- Loss: -100

## Technical Specifications

- Grid Size: 10x10
- Ship Types: Carrier, Battleship, Destroyer, Submarine, Patrol Boat
- Input Method: Mouse click
- Output Format: Visual display with JSON state (accessible via get_state_array())

## Project Structure

```
category/games/2026/02/1739025011-vector-battleship-strategic-fleet/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── board.py         - Board logic, ship placement, hit detection
├── ai.py            - Probability-based AI opponent
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
```
