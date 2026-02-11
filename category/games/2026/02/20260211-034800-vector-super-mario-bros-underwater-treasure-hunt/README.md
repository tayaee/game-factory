# Vector Super Mario Bros Underwater Treasure Hunt

Navigate the deep sea to collect coins while dodging relentless Bloopers and Cheep Cheeps.

## Description

A simplified 2D underwater platformer inspired by classic Super Mario Bros water levels. The player character is in a constant state of slowly sinking. Pressing the swim key applies an upward force to navigate through the underwater cavern. Collect coins and avoid enemies while traversing the scrolling level.

## Controls

- **SPACE / UP ARROW**: Swim upward
- **LEFT ARROW**: Move left
- **RIGHT ARROW**: Move right
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Buoyancy physics**: Player naturally sinks over time
- **Swimming**: Press swim key to apply upward force
- **Horizontal movement**: Free movement left and right
- **Auto-scrolling**: Level scrolls continuously from right to left

### Enemies

- **Bloopers** (white squids): Lunge toward player position periodically
- **Cheep Cheeps** (red fish): Swim horizontally across the screen in wave patterns
- **Coral reefs**: Static obstacles on the sea floor
- **Pipes**: Static obstacles that block passage

### Scoring

- 100 points for each coin collected
- 1 point for each unit of distance traveled
- Game over upon contact with any enemy or obstacle

## Build & Run

```bash
# Initialize and install dependencies
uv sync

# Run game
uv run python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Engine**: Pygame-ce
- **Style**: Minimalist vector art with underwater theme
- **AI Training**: Suitable for reinforcement learning with buoyancy-based physics
