# Geometric Shape Sorter Pro

A puzzle game that tests spatial perception by quickly matching geometric shapes to their corresponding holes.

## Description

Various geometric shapes (circle, triangle, square, star) fall from the top of the screen. Players must guide each shape to the matching silhouette basket at the bottom using left/right arrow keys. Speed increases over time, and wrong placements cost lives.

## How to Build

```bash
pip install pygame
```

Or using uv:

```bash
uv sync
```

## How to Start

```bash
python main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

- **Left/Right Arrow Keys**: Move the falling shape horizontally
- **Spacebar**: Fast drop the shape
- **R Key**: Restart after game over
- **ESC**: Quit the game

Match each shape to its corresponding basket to score points. Consecutive matches build combo bonuses. 3 lives - lose one for each wrong placement or missed shape.

## Examples

Successfully guide a circle to the circular basket, then quickly score with a triangle to build combos for bonus points.

## How to Cleanup

```bash
rm -rf __pycache__
```
