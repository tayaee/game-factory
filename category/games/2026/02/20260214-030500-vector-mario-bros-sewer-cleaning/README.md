# Vector Mario Bros - Sewer Cleaning

Clear the sewer of pests by flipping enemies from below in this classic arcade reimagining.

## Description

A single-screen platformer featuring a multi-tier sewer layout. Enemies (pests) emerge from pipes at the top corners and traverse the platforms toward the bottom. The player must jump and hit the platform directly beneath an enemy to flip it over, then kick the stunned enemy to remove it. If an enemy is not kicked in time, it recovers and moves faster. The game includes 'POW' blocks that flip all enemies currently touching a platform. Physics include gravity, momentum-based movement, and wrap-around screen edges (exiting left brings you in from the right).

## Game Rules

### Enemy Types
- **Shellcreeper** (standard) - One hit to flip
- **Sidestepper** - Requires two hits to flip

### Scoring
- Flip enemy: 10 points
- Kick enemy: 500 points
- Collect coin: 200 points
- Multiple kick bonus: multiplier for each enemy kicked in one stun cycle

### Lives
- 3 lives to start

### Win/Loss Conditions
- **Win**: Clear all enemies in the current wave (progresses to next wave)
- **Loss**: Touching an active (non-stunned) enemy

## How to Build

```bash
uv init && uv add pygame numpy
```

## How to Start

Windows:
```bash
run.bat
```

Linux/Mac:
```bash
./run.sh
```

Or manually:
```bash
uv run --no-active --python 3.12 main.py
```

Note: Requires Python 3.12 or earlier. Pygame does not work with Python 3.14+.

## How to Stop

Press ESC key or close the window.

## How to Play

- **LEFT/RIGHT ARROW**: Move
- **SPACE**: Jump
- **ESC**: Quit

Position yourself under an enemy's platform and jump to hit the ceiling. Once the enemy is upside down, run into it to kick it away. Score points by clearing enemies and collecting coins that emerge from pipes. Use the POW block sparingly by jumping into it from below to flip all enemies on platforms.

## AI Agent Info

### Observation Space
- Player coordinates
- Enemy coordinates/state (active/stunned)
- Platform map
- Coin positions

### Action Space
- Move Left
- Move Right
- Jump
- Idle

### Reward Structure
- Positive reward for kicking enemies and clearing waves
- Negative reward for losing a life or time decay

## Technical Requirements

- **Language**: Python 3.10+
- **Framework**: Pygame
- **Dependencies**: pygame, numpy
- **Build Tool**: uv

## Cleanup

```bash
rm -rf .venv && rm pyproject.toml uv.lock
```
