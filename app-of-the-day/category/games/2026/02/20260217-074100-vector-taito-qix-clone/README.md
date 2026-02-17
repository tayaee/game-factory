# Vector Taito Qix Clone

A territory capture arcade game where the player draws lines to enclose and capture area while avoiding enemies.

## Description

Capture the territory by drawing lines while avoiding the unpredictable spark. The game challenges spatial reasoning and risk management. It is an ideal environment for reinforcement learning agents to learn pathfinding and area maximization under dynamic constraints.

## How It Works

The game consists of a rectangular field. The player controls a marker that moves along the edges of the captured area. The player can move into the empty space to draw a "Stix" (line). If the player completes a closed loop back to an existing edge, the enclosed area is captured. A hostile entity called the "Qix" wanders randomly inside the empty space; if it touches an incomplete Stix, the player loses a life. Additionally, "Sparx" move along the edges of the captured area to chase the player. The goal is to capture at least 75% of the total area.

## Rules

- **Field Size**: 600x600 pixels (60x60 grid)
- **Win Condition**: Capture >= 75% of the total field area
- **Lose Condition**: Life count reaches zero. Lives are lost if Qix hits an unclosed line or Sparx hits the player.
- **Scoring**: Area size captured multiplied by current level speed factor.

## Technical Specifications

- **Language**: Python 3.12+
- **Library**: pygame-ce
- **Dependencies**: pygame-ce
- **Environment Management**: uv

## Installation

```bash
uv init
uv add pygame-ce
```

## How to Run

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

Or directly:
```bash
uv run main.py
```

## How to Stop

Press ESC or close the window.

## How to Play

Use arrow keys (UP, DOWN, LEFT, RIGHT) to move along edges. Hold the SPACE bar while moving to draw a line into the empty area. Release SPACE only after returning to an edge to finalize the capture. Avoid the moving Qix inside and Sparx on the boundaries. Scoring is based on the percentage of area captured.

## Cleanup

```bash
rm -rf .venv && rm pyproject.toml uv.lock
```

## Reinforcement Learning Metadata

### Action Space

- move_up
- move_down
- move_left
- move_right
- draw_modifier_hold
- draw_modifier_release

### Observation Space

2D Grid mapping (Captured Area, Current Line, Qix Position, Sparx Position, Player Position)

### Reward Function

- Positive reward for completed area capture proportional to size
- Negative reward for losing a life
- Bonus for finishing level
