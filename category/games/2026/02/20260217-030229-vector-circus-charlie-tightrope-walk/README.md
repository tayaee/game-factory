# Vector Circus Charlie Tightrope Walk

Master the art of balance and timing in this classic circus tightrope challenge.

## Description

A simplified 2D side-scroller inspired by the tightrope level of Circus Charlie. Control a circus performer walking on a high-wire from left to right. Monkeys appear from the right side and move toward the player at varying speeds. The performer must jump over these monkeys to survive. The game ends if the performer touches a monkey or falls off the rope. The goal is to reach the finish platform at the end of the rope within a time limit.

## Controls

- **RIGHT ARROW**: Move forward
- **SPACEBAR**: Jump
- **ESC**: Quit game

## Gameplay

### Mechanics

- **Manual movement**: Hold RIGHT ARROW to move forward
- **Jump timing**: Jump to avoid incoming monkeys
- **Monkeys**: Varying speeds, spawn periodically ahead of you
- **Win condition**: Reach the green goal platform at x=2000
- **Lose condition**: Collision with monkey or falling off rope

### Scoring

- Points based on distance traveled
- Bonus 100 points for each monkey successfully jumped over
- Massive bonus for reaching the goal

## Build & Run

```bash
# Initialize and install dependencies
uv venv
uv pip install pygame-ce

# Run the game
uv run --no-active --python 3.12 python main.py

# Or use the provided scripts
./run.sh        # Linux/Mac
run.bat         # Windows
```

## Cleanup

```bash
rm -rf .venv
```

## Technical Details

- **Resolution**: 800x400
- **Frame Rate**: 60 FPS
- **Style**: Minimalist vector art with high contrast colors
- **Gravity**: 0.8
- **Jump Strength**: -12
- **AI Training**: Suitable for reinforcement learning with discrete action space and temporal observation features

## Game Rules

- Performer starts at x=50, goal at x=2000
- Monkeys spawn every 2 seconds at varying distances ahead
- Monkey speeds range from 2 to 5
- Parabolic jump physics for predictable arcs
- Rope serves as the only walking plane
