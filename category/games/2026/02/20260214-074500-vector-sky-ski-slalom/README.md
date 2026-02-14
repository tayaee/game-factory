# Vector Sky Ski Slalom

Navigate a high-speed downhill descent avoiding obstacles and passing through gates.

## Description

This game focuses on precision timing, reaction speed, and path optimization. It is ideal for testing AI agents in continuous space movement and obstacle avoidance scenarios with a constant downward velocity vector.

The player controls a skier moving down a continuous slope. The screen scrolls upward at a constant speed, simulating downhill movement. Obstacles include pine trees (stationary) and moving snowmobiles. Slalom gates consist of two poles; passing between them awards bonus points. The game difficulty increases over time as the scrolling speed slightly accelerates and obstacle density grows.

## How to Build

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

## How to Play

Controls:
- LEFT/RIGHT: Move the skier horizontally
- R: Restart after game over
- ESC: Quit

Scoring:
- Points awarded for distance traveled
- +50 bonus points for each gate passed successfully
- Collision ends the game instantly

Goal: Stay alive as long as possible by avoiding trees and snowmobiles while passing through red slalom gates for bonus points.

## How to Stop

Press ESC or close the window. For CLI, use Ctrl+C.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Specifications

- Resolution: 400x600
- FPS: 60
- Framework: Pygame
- State Space: Continuous (X-position of player, X/Y of obstacles and gates)
- Action Space: Discrete (Left, Right, Stay)
- Reward Structure: Positive for time alive, high bonus for gates, negative for collisions
