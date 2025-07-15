# Particle Filter-based Visual Object Tracking Game

This project is an interactive shape-matching game that uses a particle filter for visual object tracking. The user controls an in-game object by moving a red-colored object in front of a webcam. The core of the project is a robust visual tracking algorithm that can handle noisy measurements and temporary occlusions.

## Features

-   **Real-time Object Tracking**: Utilizes a particle filter to track the user's hand movements via a red object.
-   **Interactive Gameplay**: Match the shape of your "ball" to the target shapes to score points.
-   **Dynamic Challenges**: Avoid moving obstacles whose speed increases as you level up.
-   **Power-Ups**: Collect shields for temporary protection.
-   **Engaging Feedback**: Features sound and particle effects for various in-game events.

## Project Structure

The project is organized into a modular structure for clarity and maintainability:
```
visual-object-tracking-game/
├── assets/
│   └── sounds/
├── src/
│   ├── components/
│   │   ├── ball.py
│   │   ├── target.py
│   │   └── ...
│   ├── utils/
│   │   └── red_object_detector.py
│   ├── settings.py
│   └── game.py
├── main.py
├── requirements.txt
└── README.md
```

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   A webcam

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abdulaihalidu/visual-object-tracking-game.git
    cd visual-object-tracking-game
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

1.  Run the game:
    ```bash
    python main.py
    ```

2.  Hold a **red object** in your hand and move it in front of the webcam to control the in-game ball.

3.  Guide the ball (filled shape) to the target that matches its shape (outlined shape) to score points.

4.  Avoid the moving red rectangular obstacles.

5.  Press `q` to quit the game at any time.

## Authors

-   Halidu Abdulai
-   Ahmad Kamal Baig
