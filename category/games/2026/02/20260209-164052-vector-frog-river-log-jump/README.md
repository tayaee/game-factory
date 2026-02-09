# Vector Frog River Log Jump

Cross the treacherous river by hopping on moving logs in this classic timing challenge.

## Description

This game focuses on the core river-crossing mechanic of the classic arcade genre, emphasizing velocity matching and precise spatial timing. The player controls a frog that must navigate from the bottom bank to the top goal by jumping on moving logs.

The game features a grid-based movement system where each keypress moves the frog one grid cell (40 pixels). The middle area is a river with 12 lanes, each containing logs moving at different speeds and directions. If the frog is on a log, it inherits the log's horizontal velocity. The game ends if the frog touches the water (falling off a log or missing a jump) or drifts off screen boundaries.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Play

Controls:
- Arrow keys (UP, DOWN, LEFT, RIGHT) to hop one grid cell at a time

Scoring:
- 10 points for each forward hop (UP)
- 500 points for reaching the goal

Goal: Reach the top grass area while staying on the moving logs. You have 3 lives.

Tips:
- Time your jumps carefully to land on logs
- Watch the log speed and direction before jumping
- Don't let logs carry you off screen
- The goal is the top row of the screen

## How to Stop

Press ESC or close the window

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Specs

- Resolution: 800x600
- FPS: 60
- Grid Size: 40x40 pixels
- Physics: Grid-based movement with platform velocity inheritance
- Input: Keyboard (Arrow keys, ESC)
