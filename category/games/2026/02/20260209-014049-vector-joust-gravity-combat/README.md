# Vector Joust: Gravity Combat

A simplified gravity-defying aerial duel where height and timing determine the victor.

## Description

Vector Joust is a simplified version of classic aerial combat games. Two knights on winged mounts (represented by vector shapes) fly in a 2D arena. The core mechanic is "Height Dominance": when two players collide, the one whose vertical position is higher wins the exchange.

## Features

- **Height Dominance Combat**: Collide with opponents from above to score
- **Wrap-around Screen**: Exit left, appear right
- **Physics-based Movement**: Gravity, thrust, and horizontal inertia
- **AI Opponent**: Play against a computer-controlled enemy

## Technical Specs

- **Language**: Python 3.10+
- **Framework**: Pygame-ce
- **Resolution**: 800x600
- **Physics**: Constant gravity (g), upward thrust (impulse), horizontal inertia

## How to Build

```bash
uv run pip install pygame-ce
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press ESC key or close the window.

## How to Play

**Controls:**
- UP Arrow: Flap wings (gain altitude)
- LEFT/RIGHT Arrows: Horizontal movement

**Scoring:**
- +100 points for colliding with an opponent from a higher position
- -50 points if hit from above

**Game Rules:**
- Each player has 3 lives
- Game ends when a player loses all lives
- AI agents should maximize vertical advantage before engaging

## How to Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```

## Project Structure

```
vector-joust-gravity-combat/
├── README.md
├── pyproject.toml
└── main.py
```
