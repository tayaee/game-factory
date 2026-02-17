# Vector Mappy Rhythm Run

A rhythm-based side-scrolling platformer featuring Mappy. Dash through the corridors, jumping over Nyamco cats and pits to the beat of the music.

## Description

Control Mappy as he runs automatically through corridors. Obstacles appear at intervals synchronized with a 120 BPM rhythm. Time your jumps to the beat for perfect timing and combo bonuses. The game features a dark grey grid background with neon-line characters in classic arcade style.

## Controls

- **SPACE**: Jump
- **R**: Restart game (when game over)
- **ESC**: Quit

## Gameplay

- **Jump on the beat**: Time your jumps within 50ms of the beat for a Perfect jump (+5 bonus points and 2x combo)
- **Combo system**: Perfect jumps build your combo multiplier. Miss the timing and your combo resets to 1
- **Obstacles**: Jump over Nyamco cats and avoid falling into pits
- **Scoring**: +10 points per obstacle cleared, multiplied by your current combo

## Scoring

- 10 points per obstacle cleared (multiplied by combo)
- +5 bonus points for Perfect jumps
- Combo multiplier increases with consecutive Perfect jumps
- Early or late jumps reset the combo

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py

# Or use the provided scripts:
# Windows: run.bat
# Linux/Mac: run.sh
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Resolution**: 800x400
- **Frame Rate**: 60 FPS
- **BPM**: 120
- **Perfect Window**: 50ms
- **State Space**: Player Y position, next obstacle distance, next obstacle type, rhythm offset
- **AI Training**: Suitable for reinforcement learning agents testing precision timing and rhythm synchronization

## Reward Function (AI Training)

- Survival: +0.1 per frame
- Successful jump: +10.0
- Perfect timing bonus: +5.0
- Collision penalty: -50.0
