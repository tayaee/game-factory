# Lunar Lander Physics Lite

Guide your lander to a safe landing on the lunar surface.

## Description

A physics-based game where you must control a lunar lander and safely land on a flat platform. The lander is affected by gravity and you have limited fuel to make a controlled descent.

## Features

- Realistic gravity physics simulation
- Limited fuel management
- Procedurally generated terrain with random landing pad position
- Speed and altitude indicators
- Touch and keyboard controls
- Score based on remaining fuel and landing quality

## How to Run

Open `index.html` in a web browser.

## Controls

- **Space** or **Click/Tap**: Fire main engine (thrust)

## Scoring

- Successful landing requires speed below 2.0 m/s and proper alignment
- Score is calculated based on:
  - Remaining fuel (10 points per unit)
  - Landing speed (softer landing = more points)
  - Landing angle (upright landing = bonus points)

## Landing Requirements

- Vertical speed must be below 2.0 m/s
- Land on the flat green platform
- Keep the lander upright

## Tech Stack

- HTML5 Canvas
- CSS3
- Vanilla JavaScript (ES6+)
