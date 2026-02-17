# Vector Volfied Area Capture

Navigate the void and claim your territory while dodging lethal cosmic entities.

## Description

Vector Volfied Area Capture is inspired by classic arcade games like Qix and Volfied. Control your Shield craft along the perimeter of claimed territory, then venture into the void to claim new areas. Draw lines to enclose regions, but beware - the Boss entity and Sparks patrol the unclaimed space. If they touch your trail before you complete an area, you lose a life. Claim at least 80% of the field to advance to the next level.

## Features

- Classic area capture gameplay with vector-style graphics
- Progressive difficulty - enemies speed up each level
- Risk/reward scoring - larger captures give exponential bonuses
- Three lives system with strategic death penalties
- Visual progress bar tracking claimed percentage
- Smooth 60 FPS gameplay

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Unix: `./run.sh`

## How to Stop

Press ESC or close the game window.

## Controls

- **Arrow Keys**: Move the Shield craft along borders and into open space
- **R**: Restart after game over / Next level after completing a level
- **ESC**: Quit game

## How to Play

1. Start on the border of the field (marked by the blue line)
2. Move into the open space using arrow keys to draw a yellow trail
3. Return to any claimed border to claim the enclosed area
4. Avoid the Boss (red cross) - it destroys your trail on contact
5. Avoid the Sparks (orange dots) - they hunt along the borders
6. Claim 80% of the total area to complete the level

## Scoring

- Area captured: Points based on captured area size
- Size multiplier: Up to 2x bonus for large captures
- Death penalty: -500 points per life lost
- Level complete bonus: +1000 points multiplied by current level

## Tips

- Make small captures first to reduce enemy movement space
- Time your draws when the Boss and Sparks are far away
- Watch all Sparks - they patrol different sides of the field
- Larger captures give higher multipliers but are riskier
