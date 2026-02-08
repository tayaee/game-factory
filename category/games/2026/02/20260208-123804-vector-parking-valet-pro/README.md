# Vector Parking Valet Pro

Master the art of precision driving and navigation in this minimalist top-down parking simulator.

## Description

A 2D top-down parking game where the player controls a vehicle in a parking lot filled with obstacles, other parked cars, and designated parking spots. The vehicle uses realistic steering physics where the turn radius is dependent on movement speed. Features multiple levels of increasing complexity including tight corners, narrow passages, and reversing requirements.

## Rationale

This game focuses on spatial awareness and fine motor control, targeting casual gamers and AI agents learning precision pathfinding under constraints. It provides a unique challenge compared to typical racing games by rewarding patience and accuracy over raw speed.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press ESC in game or close the window.

## How to Play

Navigate the car from the starting position to the highlighted parking spot and come to a complete stop within the lines.

**Controls:**
- UP arrow - Accelerate forward
- DOWN arrow - Brake / Reverse
- LEFT/RIGHT arrows - Steer the front wheels
- SPACE - Start game / Continue
- ESC - Return to menu / Quit

**Scoring:**
- Base score: 1000 points
- Time bonus: +10 points per second remaining
- Distance penalty: -1 point per 10 pixels traveled
- Park accurately and quickly for the highest score

## Technical Specifications

- **Engine:** Pygame-ce (Community Edition)
- **Physics:** Vector-based movement with momentum and rotation limits
- **State representation:** Car coordinates, heading angle, obstacle distance sensors (raycasting), and target coordinates

## AI Integration

### Observation Space
```python
{
    "car_x": float,           # Normalized 0-1
    "car_y": float,           # Normalized 0-1
    "car_angle": float,       # Normalized 0-1
    "car_speed": float,       # Normalized 0-1
    "target_dist": float,     # Normalized distance
    "target_angle": float,    # Angle to target in radians
    "sensors": [float],       # 8 raycast sensor readings 0-1
    "time_remaining": float,  # Normalized 0-1
    "game_state": str         # Current state
}
```

### Action Space
```python
{
    "accelerate": float,  # 0-1
    "brake": float,       # 0-1
    "left": float,        # 0-1
    "right": float        # 0-1
}
```

### Reward Function
- **Positive rewards:**
  - Reaching target: +100
  - Aligning with parking angle: +0 to +50 based on accuracy
  - Distance reduction to target: +0.1 per frame
- **Negative rewards:**
  - Collision: -100
  - Time penalty: -0.01 per frame
  - Excessive steering changes: -0.05

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
