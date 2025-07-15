import numpy as np
import os

# Screen Dimensions
WIDTH, HEIGHT = 1280, 720
CANVAS_SIZE = (HEIGHT, WIDTH, 3)

# Colors (BGR format for OpenCV)
COLORS = {
    "ball": (225, 105, 65),
    "target_outline": (225, 105, 65),
    "obstacle": (0, 0, 255),
    "powerup_shield": (0, 255, 255),
    "effect_success": (0, 255, 0),
    "effect_fail": (0, 0, 255),
    "effect_powerup": (0, 215, 255),
    "effect_default": (255, 255, 255)
}

# UI Text Settings
UI_TEXT_FONT = 1 # cv2.FONT_HERSHEY_SIMPLEX
UI_TEXT_SCALE = 1
UI_TEXT_THICKNESS = 2
UI_COLORS = {
    "score": (128, 128, 0),
    "hearts": (0, 0, 255),
    "level": (130, 0, 75),
    "combo": (130, 0, 75),
    "shield": (0, 255, 0),
    "game_over": (0, 0, 255)
}

# Particle Filter Settings
NUM_PARTICLES = 300
MOTION_NOISE = 10
ACCELERATION_NOISE = 2
PARTICLE_SIGMA = 50.0

# Game Object Shapes
SHAPES = ["circle", "square", "triangle", "rectangle"]

# Ball and Target Parameters
BALL_PARAMS = {
    "circle": {"radius": 50},
    "square": {"side": 60},
    "rectangle": {"width": 80, "height": 50},
    "triangle": {"side": 60}
}
TARGET_PARAMS = {
    "circle": {"radius": 70},
    "square": {"side": 100},
    "rectangle": {"width": 120, "height": 80},
    "triangle": {"side": 100}
}

# Red Object Detection HSV Ranges
RED_LOWER1 = np.array([0, 120, 70])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([170, 120, 70])
RED_UPPER2 = np.array([180, 255, 255])

# Audio files
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS = {
    "score": os.path.join(ROOT_DIR, "assets", "sounds", "score.wav"),
    "penalty": os.path.join(ROOT_DIR, "assets", "sounds", "penalty.mp3"),
    "levelup": os.path.join(ROOT_DIR, "assets", "sounds", "levelup.mp3"),
    "powerup": os.path.join(ROOT_DIR, "assets", "sounds", "Powerup.wav"),
    "combo": os.path.join(ROOT_DIR, "assets", "sounds", "combo.wav")
}