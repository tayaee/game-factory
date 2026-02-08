# Vector Plumber Pipe Connector

Rotate and connect pipe segments to create a seamless flow from source to drain.

## Description

This puzzle game targets logic enthusiasts and provides a clear objective for reinforcement learning agents to optimize pathfinding and topological connectivity in a grid-based environment.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

Press ESC or close the window.

## How to Play

**Goal**: Connect the Source (IN) pipe to the Drain (OUT) pipe.

**Controls**:
- Left-click on a grid cell to rotate the pipe segment 90 degrees clockwise
- SPACE: Generate new level
- ESC: Quit

**Scoring**: Complete levels quickly with fewer rotations for better efficiency.

## AI Integration

**State Representation**: 7x7 integer array where each integer encodes pipe type and rotation state (0-3).

**Action Space**: 49 actions (one for each cell). Selecting a cell triggers one rotation.

**Reward Structure**:
- +100 for connecting source to drain
- -1 per rotation
- -0.1 per second elapsed (encourages efficiency)

## Project Structure

```
category/
└── games/
    └── 2026/
        └── 02/
            └── 1739023920-vector-plumber-pipe-connector/
                ├── main.py
                ├── game.py
                ├── config.py
                ├── pyproject.toml
                ├── README.md
                └── appinfo.json
```

## How to Cleanup

```bash
rm -rf .venv
```
