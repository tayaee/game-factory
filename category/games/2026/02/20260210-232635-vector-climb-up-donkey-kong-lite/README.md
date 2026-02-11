# Vector Climb Up - Donkey Kong Lite

Scale the construction site while dodging rolling barrels in this classic arcade-inspired challenge.

## Description

This game focuses on timing, vertical movement, and collision avoidance. It provides a perfect environment for AI agents to learn jump timing and pathfinding in a 2D platforming space with dynamic hazards.

## Game Details

The game consists of a single-screen construction site with four levels of horizontal girders connected by ladders. The player starts at the bottom-left and must reach the top-right platform. An antagonist at the top releases barrels that roll down the girders and fall down ladders or off edges. Barrels follow a gravity-based movement pattern. The player can walk left/right, climb ladders when aligned, and jump over barrels. Collision with a barrel results in an immediate game over. The game environment is rendered using vector-style graphics with a professional dark theme.

## How to Build

```bash
uv venv
uv pip install pygame
```

Or simply:
```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC in the game window, or close the window.

## How to Play

**Goal**: Reach the goal platform at the top.

**Scoring**:
- +10 points for every barrel jumped over
- +500 points for reaching the goal

**Controls**:
- Left/Right Arrow keys to move
- Up/Down Arrow keys to climb ladders
- Spacebar to jump
- ESC to quit

**AI Input**: The agent should monitor the x,y coordinates of the player and all active barrels.

## Technical Specs

- **Framework**: Pygame
- **Resolution**: 800x600
- **FPS**: 60

**State Space**:
- player_pos
- barrel_positions
- on_ladder_flag
- is_jumping_flag

**Action Space**:
- move_left
- move_right
- climb_up
- climb_down
- jump
- idle

## How to Cleanup

```bash
rm -rf .venv
find . -type d -name '__pycache__' -exec rm -rf {} +
```
