# Vector Qix - Area Capture

Claim territory while dodging the deadly geometric flicker in this classic arcade reimagining.

## Description

Inspired by the classic arcade game Qix, Vector Qix challenges you to claim territory by drawing lines across an open field. Control your marker along the borders, then venture into the open space to enclose areas. But beware - the Qix, a wandering entity of flickering lines, roams the unclaimed space. If it touches your trail while you're drawing, you lose a life. Two Sparks also patrol the borders, hunting for careless players.

## Features

- Classic Qix gameplay with vector-style graphics
- Progressive difficulty - enemies speed up each level
- Risk/reward scoring system - capture farther from the Qix for multipliers
- Multiple lives system with death penalties
- Visual progress bar showing claimed percentage
- Smooth 60 FPS gameplay

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run main.py
```

## How to Stop

Press ESC or close the game window.

## Controls

- **Arrow Keys**: Move the marker along borders and into open space
- **Space (hold)**: Draw a trail while moving
- **R**: Restart after game over
- **ESC**: Quit game

## How to Play

1. Start on the border of the field
2. Move into the open space while holding SPACE to draw a trail
3. Return to any border to claim the enclosed area
4. Avoid the Qix (magenta flickering lines) - it will destroy your trail
5. Avoid the Sparks (orange dots) - they patrol the borders
6. Claim 75% of the area to complete the level

## Scoring

- Area captured: +10 points per 1% of total area
- Risk multiplier: Up to 2x based on distance from Qix during capture
- Death penalty: -500 points
- Level complete bonus: +2000 points

## Tips

- Make small captures first to reduce the Qix's movement space
- Time your draws when the Qix is far away
- Watch both Sparks - they move in opposite directions along borders
- Larger captures give higher risk multipliers but are more dangerous
