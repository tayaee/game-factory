# Vector Frog Jump Safe

A timing-based action game where you navigate a frog across roads and rivers to reach safety.

## Description

Guide your frog from the starting point at the bottom of the screen to the safe goal zone at the top. Navigate through multiple lanes of traffic (roads with cars) and water hazards (rivers with floating logs). Each lane has obstacles moving at different speeds and directions. Time your movements carefully to avoid cars and stay on logs when crossing water.

## Features

- Grid-based movement with arrow keys
- Multiple lanes with varying obstacle speeds and directions
- Road lanes with cars to avoid
- River lanes requiring you to ride floating logs
- Progressive difficulty - levels increase obstacle speed
- Score tracking with 100 points per level completion

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run python main.py
```

## How to Stop

Close the game window or press Alt+F4.

## Controls

- **Up Arrow**: Move one grid space forward
- **Down Arrow**: Move one grid space backward
- **Left Arrow**: Move one grid space left
- **Right Arrow**: Move one grid space right
- **Space**: Restart after game over or winning a level

## Rules

- Avoid all cars on the road - touching a car ends the game
- On rivers, you must be on a log to survive - falling in water ends the game
- Logs move, carrying you with them - don't float off screen
- Reach the GOAL zone at the top to score 100 points and advance to the next level
- Each level increases obstacle speeds

## Examples

Quickly tap Up to dash across fast-moving traffic lanes, then pause at the riverbank to time your jumps onto moving logs. Ride each log carefully and hop to the next one until you reach the safety of the goal zone.

## How to Cleanup

```bash
rm -rf __pycache__
```
