# AI-Draw-Guess-Battle

An interactive anime character display project using Python, Pygame, and Live2D concepts.

## Project Overview

This project demonstrates how to create interactive anime-style characters with Live2D-like behavior using Python and Pygame. While not using the actual Live2D Cubism SDK, it simulates many of the visual effects and interactive features you would see in a real Live2D implementation.

## Features

- Multiple animated anime characters with realistic movement
- Emotion system with 6 different expressions
- Interactive controls for character manipulation
- Particle effects for visual feedback
- Customizable character color schemes
- Word database integration for game elements
- Smooth animations including breathing and blinking effects

## Directory Structure

```
.
├── game/                 # Main game implementation
│   ├── main.py          # Main game file with character display logic
│   ├── README.md        # Game-specific documentation
│   └── requirements.txt # Python dependencies
├── words.json           # Word database for game elements
└── README.md            # This file
```

## Requirements

- Python 3.6+
- Pygame 2.5.2
- NumPy 1.24.3

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv game/venv
   source game/venv/bin/activate  # On Windows: game\venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r game/requirements.txt
   ```

## Running the Project

Navigate to the project directory and run:
```bash
python game/main.py
```

## Controls

- **Arrow Keys**: Move active character left/right and scale up/down
- **Space**: Change character emotion randomly
- **Enter**: Cycle through words from the database
- **Tab**: Switch between characters
- **C**: Change character color scheme
- **Escape**: Quit the application

## Technical Notes

This implementation simulates Live2D behavior using Pygame's drawing capabilities. In a production environment with actual Live2D integration, you would need:

1. The official Live2D Cubism SDK
2. Actual Live2D model files (.moc3, .model3.json, etc.)
3. Proper integration with the Cubism SDK

The simulation includes:
- Character animation with breathing and blinking
- Emotion-based facial expressions
- Interactive character manipulation
- Visual effects and feedback

## Extending the Project

To convert this simulation to use actual Live2D models:

1. Obtain the Live2D Cubism Editor and create/acquire models
2. Export models in the Cubism format
3. Integrate the Cubism SDK for native applications
4. Replace the Live2DCharacter class with actual Live2D rendering code

For more information on Live2D Cubism SDK, visit the [official website](https://www.live2d.com/en/download/cubism-sdk/).