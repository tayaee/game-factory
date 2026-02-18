# Vector Fire Extinguish Logic

Tactical water-pressure puzzle to extinguish spreading flames in a grid warehouse.

## Description

A strategic resource management puzzle where you control a fire-extinguishing bot in a burning warehouse. Fire spreads to adjacent flammable boxes every 5 seconds. Navigate the 10x10 grid, extinguish fires with limited water, and refill at water stations located in the corners. Balance speed and efficiency to save as many boxes as possible.

## Controls

- **Arrow Keys**: Move the bot
- **SPACE**: Extinguish fire at current position
- **R**: Restart game
- **ESC**: Quit

## Gameplay

- **Fire Spread**: Fire spreads to adjacent flammable cells every 5 seconds
- **Water Management**: You have 5 units of water. Each extinguish costs 1 unit
- **Refill Stations**: Blue squares at the four corners refill your water to full capacity
- **Scoring**: +100 points per extinguished box, -10 points per box lost to fire
- **Objective**: Maximize saved boxes and minimize fire spread

## Game Features

- Procedurally generated warehouse layouts
- Real-time fire spread mechanics
- Resource management with water capacity
- Vector-style minimalist graphics
- Suitable for RL agent training

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run --no-active --python 3.12 python main.py

# Or use the provided scripts:
# Windows: run.bat
# Linux/Mac: run.sh
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Grid Size**: 10x10
- **Resolution**: 800x700
- **Frame Rate**: 60 FPS
- **Fire Spread Interval**: 5 seconds
- **Water Capacity**: 5 units
- **Extinguish Time**: 0.5 seconds per cell

## RL Training

### Observation Space

10x10 grid matrix with integer values:
- 0: Empty floor
- 1: Flammable box
- 2: Fire
- 3: Obstacle/Wall
- 4: Bot position
- 5: Refill station

### Action Space

Discrete actions:
- 0: Move Up
- 1: Move Down
- 2: Move Left
- 3: Move Right
- 4: Extinguish

### Reward Function

- Extinguish a fire: +100
- Box lost to fire: -10

### Training Tips

The game requires balancing pathfinding efficiency with resource management. Agents should learn to:
1. Prioritize fires with most adjacent flammable cells
2. Plan routes to minimize travel time
3. Coordinate water refills strategically
4. Consider fire spread prediction in decision making
