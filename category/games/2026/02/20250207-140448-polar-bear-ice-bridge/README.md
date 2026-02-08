# Polar Bear Ice Bridge

A timing-based physics puzzle game where you build bridges to help a polar bear cross ice floes.

## Description

Guide the polar bear across the frozen ocean by building bridges at the right length. Hold to extend your bridge, release to drop it. If the bridge lands perfectly on the next ice floe, the bear crosses safely. Miss the target and the bear falls into the freezing water.

## Features

- Simple one-button control - hold to build, release to drop
- Progressive difficulty with randomized platform distances and widths
- Bonus points for perfect center landings
- Adorable polar bear character with smooth animations
- Atmospheric arctic environment with animated waves

## How to Build

Built with HTML5 Canvas and vanilla JavaScript. No external libraries required.

## How to Run

1. Install dependencies: `uv sync`
2. Run the server: `uv run python main.py`
3. Open your browser to: `http://127.0.0.1:5000`

## Controls

- **Desktop**: Hold SPACE or CLICK to extend bridge, release to drop
- **Mobile**: Touch and hold to extend bridge, release to drop

## Scoring

- Successfully land on the next platform: +1 point
- Perfect center landing: +1 bonus point
- Game ends when the bridge misses the platform

## Examples

- Time your bridge extension carefully - too short and you fall, too long and you overshoot
- Aim for the center of each platform for bonus points
- As you progress, platforms become smaller and further apart
