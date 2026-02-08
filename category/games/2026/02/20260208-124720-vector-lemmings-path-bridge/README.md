# Vector Lemmings: Path Bridge

Guide a group of autonomous explorers to the exit by assigning critical path-finding roles.

## Description

A simplified Lemmings-style puzzle game where indirect control and strategic resource management are key. Agents spawn from an entry point and walk in a straight line until hitting obstacles. You must assign skills at critical moments to guide them to the exit portal.

## Rationale

This game focuses on indirect control and strategic resource management. It targets players who enjoy puzzle-solving and logic, and provides an excellent environment for AI agents to learn time-sensitive decision making and spatial planning.

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Run

```bash
uv run main.py
```

## Controls

| Key | Action |
|-----|--------|
| 1 | Select Blocker skill |
| 2 | Select Builder skill |
| 3 | Select Basher skill |
| Left Click | Apply selected skill to agent |
| SPACE | Start game / Restart |
| ESC | Quit |

## Skills

| Skill | Description | Uses |
|-------|-------------|------|
| Blocker | Stops other agents from passing (radius collision) | 2 |
| Builder | Creates diagonal path upward (5 up over 10 across) | 5 |
| Basher | Digs horizontally through walls | 5 |

## How to Win

Save at least 50% of agents (8 out of 15) by guiding them to the purple exit portal before time runs out.

## Technical Specifications

- **Language**: Python 3.12+
- **Library**: Pygame-ce
- **Resolution**: 800x600
- **State Representation**: 2D Integer Array (Grid)
- **Action Space**: Discrete(agent_index, skill_id)

## How to Stop

Press ESC or close the window.

## How to Cleanup

```bash
rm -rf .venv
```

## AI Integration

The game exposes AI-friendly interfaces:

- `get_observation()`: Returns current game state including agent positions, skills remaining, and time
- `step_ai(action)`: Execute actions with (agent_index, skill_id) tuple

Reward Structure:
- Agent saved: +10.0
- Agent died: -5.0
- Win: +50.0
- Lose: -20.0
- Per frame: +0.01
