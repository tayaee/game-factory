# Vector Super Mario Bros Underwater Dash

Navigate Mario through a dangerous underwater cavern filled with Bloopers and Cheep Cheeps.

## Description

This game focuses on the unique physics of underwater navigation. The player controls a character with buoyancy mechanics - constant input is required to stay afloat. The underwater environment features high drag, low gravity, and momentum-based movement that differs significantly from land-based platformers.

The game is a 2D side-scrolling underwater action game. Key features include: buoyancy-based physics where the player slowly sinks and must swim to stay afloat; high drag that limits movement speed; Bloopers that patrol vertically with wavy patterns; Cheep Cheeps that swim horizontally across the screen; coins that bob gently in the water current; platforms that create navigation challenges; and a goal flag at the right end of the level.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Play

Controls:
- LEFT/RIGHT Arrow keys: Move horizontally
- SPACE or UP Arrow: Swim upward (overcomes gravity)

Scoring:
- 100 points per coin collected
- 500 points for finishing the level
- 0 points if you die (score resets)

Goal: Reach the flagpole at the right end of the level while avoiding enemies.

Enemies:
- Bloopers: White squid-like creatures that move vertically
- Cheep Cheeps: Orange fish that swim horizontally

## How to Stop

Ctrl+C or close the window

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specs

- Resolution: 800x600
- FPS: 60
- Physics: Buoyancy-based with high drag (0.92) and low gravity (300)
- Input: Keyboard (Arrow keys, Space, Up)
- State Space: Player position, velocity, enemy positions, coin positions
- Action Space: LEFT, RIGHT, SWIM, IDLE
