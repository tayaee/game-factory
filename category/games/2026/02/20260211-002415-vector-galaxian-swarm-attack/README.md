# Vector Galaxian Swarm Attack

Defend the starship against tactical alien swarms in this high-intensity vector shooter.

## Description

Classic fixed shooter inspired by Galaxian featuring complex enemy maneuvers. Unlike static shooters, individual aliens or small groups break formation and dive toward the player in curved paths. Features state-machine based enemy AI with three enemy types: Drones (bottom tier), Emissaries (middle), and Flagships (top).

## Technical Specifications

- **Language**: Python 3.12+
- **Rendering**: pygame-ce
- **Environment**: 600x800 grid
- **Physics**: Bezier-curve movement for diving enemies

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Start

```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# Or directly
uv run --no-active --python 3.12 python main.py
```

## How to Stop

Press ESC to quit, or close the window.

## How to Play

- **Arrow Keys** or **A/D**: Move ship left/right
- **SPACE**: Fire

### Scoring

| Enemy | Formation | Diving |
|-------|-----------|--------|
| Drone | 30 pts | 60 pts |
| Emissary | 50 pts | 100 pts |
| Flagship | 150 pts | Bonus |

**Bonus**: Destroy a Flagship with its escorts for +300 points.

### Goal

Clear all 3 waves by destroying aliens while avoiding their attacks. Prioritize diving targets for double points. Surviving earns you nothing—eliminate the swarm!

## How to Cleanup

```bash
rm -rf .venv
find . -type d -name '__pycache__' -exec rm -rf {} +
```

## Reward Structure (RL)

- Hit enemy: +1.0
- Clear wave: +10.0
- Player death: -5.0
- Time penalty: -0.01/frame
