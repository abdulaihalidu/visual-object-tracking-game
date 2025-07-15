import cv2
import numpy as np
import random
from typing import Tuple

from src.settings import COLORS
from src.components.ball import Ball

class Obstacle:
    """
    Represents a moving rectangular obstacle. Its velocity increases with the game level.
    """
    def __init__(self, canvas_size: Tuple[int, int, int], level: int):
        self.canvas_size = canvas_size
        self.size = (random.randint(50, 100), random.randint(50, 100))
        self.position = np.array([
            random.randint(0, canvas_size[1] - self.size[0]),
            random.randint(0, canvas_size[0] - self.size[1])
        ], dtype=float)
        speed_factor = 1 + (level - 1) * 0.2
        self.velocity = np.array([
            random.choice([-3, 3]) * speed_factor,
            random.choice([-3, 3]) * speed_factor
        ], dtype=float)
        self.color = COLORS["obstacle"]

    def update(self):
        """Updates the obstacle's position and handles boundary collisions."""
        self.position += self.velocity
        if self.position[0] <= 0 or self.position[0] + self.size[0] >= self.canvas_size[1]:
            self.velocity[0] *= -1
        if self.position[1] <= 0 or self.position[1] + self.size[1] >= self.canvas_size[0]:
            self.velocity[1] *= -1

    def draw(self, frame: np.ndarray):
        top_left = self.position.astype(int)
        bottom_right = (self.position + self.size).astype(int)
        cv2.rectangle(frame, tuple(top_left), tuple(bottom_right), self.color, -1)

    def collides_with(self, ball: Ball) -> bool:
        """Checks for collision between the obstacle and the ball."""
        ball_pos = ball.get_position()
        x, y = self.position
        w, h = self.size
        return (x <= ball_pos[0] <= x + w) and (y <= ball_pos[1] <= y + h)