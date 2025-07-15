import cv2
import numpy as np
import random
from typing import Tuple

from src.settings import COLORS

class PowerUp:
    """
    Represents a power-up object that grants a temporary shield.
    """
    def __init__(self, canvas_size: Tuple[int, int, int]):
        self.canvas_size = canvas_size
        self.radius = 25
        self.position = np.array([
            random.randint(self.radius, canvas_size[1] - self.radius),
            random.randint(self.radius, canvas_size[0] - self.radius)
        ], dtype=int)
        self.type = "shield"
        self.duration = 300  # in frames
        self.color = COLORS["powerup_shield"]

    def draw(self, frame: np.ndarray):
        cv2.circle(frame, tuple(self.position), self.radius, self.color, -1)
        cv2.circle(frame, tuple(self.position), self.radius, (255,255,255), 2)