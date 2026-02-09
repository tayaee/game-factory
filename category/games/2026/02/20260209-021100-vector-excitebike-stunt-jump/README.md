# Vector Excitebike Stunt Jump

Master the rhythm of the track and perform perfect mid-air stunts in this physics-based motocross challenge.

## Description

A side-scrolling motocross racer inspired by the classic Excitebike. Race against time across a dynamically generated track filled with ramps, hurdles, and mud pits. Manage your engine heat while performing aerial stunts to maximize distance.

## Controls

- **RIGHT Arrow**: Accelerate
- **Z**: Turbo boost (increases speed but builds heat)
- **UP/DOWN Arrows**: Change lanes (3 lanes available)
- **LEFT/RIGHT Arrows**: Tilt bike while airborne
- **SPACE**: Start game from menu
- **R**: Restart after game over
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Acceleration**: Hold RIGHT to accelerate normally, press Z for turbo boost
- **Heat Management**: Turbo increases engine temperature. Overheat and you'll stall for several seconds
- **Tilt Control**: Adjust bike angle in mid-air to land smoothly
- **Lanes**: Switch between 3 lanes to avoid obstacles

### Track Elements

- **Flat sections**: Normal riding surface
- **Ramps**: Launch you into the air for stunts
- **Mud pits**: Slow you down significantly
- **Hurdles**: Barriers that can crash you at low speed

### Landing

Land with your bike parallel to the ground (flat) to:
- Maintain speed
- Avoid crashing
- Continue acceleration smoothly

## Scoring

- Points awarded for distance traveled (10 points per meter)
- Game ends after 120 seconds
- Crashing ends the run immediately
- Try to cover maximum distance within the time limit

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Game Loop Frequency**: 60Hz
- **Input Space**: Discrete actions for acceleration, turbo, and tilt control
- **Observation Space**: RGB pixel array or vector state (distance, speed, heat, pitch, obstacle type)
- **AI Training**: Suitable for reinforcement learning agents learning physics-based control and resource management
