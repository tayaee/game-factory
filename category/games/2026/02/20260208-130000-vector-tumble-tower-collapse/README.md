# Vector Tumble Tower Collapse

Strategic precision physics puzzle inspired by the classic wooden block stacking challenge.

## Description

A physics-based tower collapse game where you carefully remove blocks from the tower and place them on top without causing collapse. The tower consists of 18 layers with 3 blocks each, arranged in alternating orientations.

## Rationale

This game targets players and AI agents interested in physics-based simulation and strategic risk-taking. It provides a controlled environment for testing spatial reasoning and stability prediction.

## Details

The game simulates a tower consisting of 18 layers, each layer having 3 rectangular blocks placed perpendicularly to the layer below. The game uses a custom physics engine with gravity, friction, and rigid body collision. Blocks are rendered as rectangles with 3D effect. The goal is to remove one block at a time and place it on the top layer without causing the tower to fall. A "fall" is defined when any block other than the one currently being moved touches the ground plane or if the tower's center of gravity shifts beyond the base limits. The game ends when the tower collapses.

## Build

```bash
uv sync
```

## Run

```bash
uv run python main.py
```

## Stop

Press `ESC` or close the window. For agents, send SIGINT.

## How to Play

1. Click a block from any layer except the top-most layer to select it
2. Drag the block horizontally to pull it out of the tower
3. Once removed, drag the block to the designated drop zone at the top of the tower
4. Release the mouse button to place it

**Scoring:**
- +10 points for every successfully relocated block
- -100 penalty for tower collapse

**Controls:**
- Mouse Left Click - Select and drag blocks
- ESC - Quit game
- SPACE - Restart (after game over)

## Features

- 18-layer tower with alternating block orientations
- Custom physics engine with gravity, friction, and collision
- Stability indicator showing tower integrity
- Center of mass calculation for realistic collapse detection
- Visual 3D effect on blocks
- Drop zone indicator at tower top

## AI Agent Input

For RL agent control:

**Observation Space:**
- Block positions (x, y, rotation) for all blocks
- Current tower height
- Center of mass vector (x, y)
- Stability score (0.0 to 1.0)

**Action Space:**
- Discrete: block_index (0 to N-1) to select
- Continuous: (target_x, target_y) for placement (0.0 to 1.0 normalized)

**Reward Structure:**
- +10 per successfully placed block
- +0.1 per stable frame
- -0.5 per unstable frame
- -100 on collapse

## Project Structure

```
category/games/2026/02/20260208-130000-000-vector-tumble-tower-collapse/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── physics.py       - Physics engine (Block, PhysicsEngine)
├── tower.py         - Tower management (Tower class)
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Cleanup

```bash
rm -rf .venv
```
