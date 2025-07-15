import cv2
import numpy as np
import random
from typing import Tuple, List, Optional, Dict

from src.settings import (
    CANVAS_SIZE, PARTICLE_SIGMA, ACCELERATION_NOISE, COLORS
)

class Ball:
    """
    Represents the game ball tracked by a particle filter.
    Each particle's state is [x, y, vx, vy].
    """
    def __init__(self, canvas_size: Tuple[int, int, int], ball_params: Dict, shapes: List[str], num_particles: int):
        self.canvas_size = canvas_size
        self.ball_params = ball_params
        self.num_particles = num_particles
        self.shape = random.choice(shapes)
        self.color = COLORS["ball"]
        self.position = self._init_position()
        self.particles = self._init_particles()

    def _init_position(self) -> np.ndarray:
        if self.shape == "circle":
            r = self.ball_params["circle"]["radius"]
            x = random.randint(r, self.canvas_size[1] - r)
            y = random.randint(r, self.canvas_size[0] - r)
        elif self.shape == "square":
            s = self.ball_params["square"]["side"]
            x = random.randint(s // 2, self.canvas_size[1] - s // 2)
            y = random.randint(s // 2, self.canvas_size[0] - s // 2)
        elif self.shape == "rectangle":
            w = self.ball_params["rectangle"]["width"]
            h = self.ball_params["rectangle"]["height"]
            x = random.randint(w // 2, self.canvas_size[1] - w // 2)
            y = random.randint(h // 2, self.canvas_size[0] - h // 2)
        elif self.shape == "triangle":
            s = self.ball_params["triangle"]["side"]
            x = random.randint(s, self.canvas_size[1] - s)
            y = random.randint(s, self.canvas_size[0] - s)
        return np.array([x, y])

    def _init_particles(self) -> np.ndarray:
        particles = np.zeros((self.num_particles, 4))
        particles[:, :2] = np.random.randn(self.num_particles, 2) * 20 + self.position
        particles[:, 2:] = np.random.randn(self.num_particles, 2) * 5
        return particles

    def update(self, measurement: Optional[np.ndarray], motion_noise: float, accel_noise: float):
        # Prediction Step
        self.particles[:, :2] += self.particles[:, 2:] + np.random.randn(self.num_particles, 2) * motion_noise
        self.particles[:, 2:] += np.random.randn(self.num_particles, 2) * accel_noise

        # Boundary collision
        self.particles[:, 0] = np.clip(self.particles[:, 0], 0, self.canvas_size[1] - 1)
        self.particles[:, 1] = np.clip(self.particles[:, 1], 0, self.canvas_size[0] - 1)

        left_collision = self.particles[:, 0] == 0
        right_collision = self.particles[:, 0] == self.canvas_size[1] - 1
        top_collision = self.particles[:, 1] == 0
        bottom_collision = self.particles[:, 1] == self.canvas_size[0] - 1

        self.particles[left_collision | right_collision, 2] *= -1
        self.particles[top_collision | bottom_collision, 3] *= -1

        # Correction (Update) Step
        if measurement is not None:
            distances = np.linalg.norm(self.particles[:, :2] - measurement, axis=1)
            weights = np.exp(-(distances ** 2) / (2 * PARTICLE_SIGMA ** 2))
            
            if np.sum(weights) > 0:
                weights /= np.sum(weights)
            else:
                weights = np.ones(self.num_particles) / self.num_particles

            # Resampling
            effective_N = 1.0 / np.sum(weights ** 2)
            if effective_N < self.num_particles / 2.0:
                indices = np.random.choice(self.num_particles, size=self.num_particles, p=weights)
                self.particles = self.particles[indices]
                self.particles[:, 2:] += np.random.randn(self.num_particles, 2) * accel_noise

    
    def get_radius(self) -> int:
        """Returns the effective radius for collision detection based on the shape."""
        if self.shape == "circle":
            return self.ball_params["circle"]["radius"]
        # For non-circular shapes, approximate a bounding radius
        elif self.shape == "square":
            return self.ball_params["square"]["side"] // 2
        elif self.shape == "rectangle":
            w = self.ball_params["rectangle"]["width"]
            h = self.ball_params["rectangle"]["height"]
            return int(np.sqrt(w**2 + h**2) / 2)
        elif self.shape == "triangle":
            return int(self.ball_params["triangle"]["side"] * 0.5)
        return 30 # Default fallback
    
    def get_position(self) -> np.ndarray:
        return np.mean(self.particles[:, :2], axis=0)


    def draw(self, frame: np.ndarray):
        # (Optional) Draw particles for debugging/visualization.
        for p in self.particles:
            cv2.circle(frame, (int(p[0]), int(p[1])), 2, (100, 0, 0), -1)

        pos = self.get_position().astype(int)
        # Draw the main ball shape over the particles
        if self.shape == "circle":
            r = self.ball_params["circle"]["radius"]
            cv2.circle(frame, tuple(pos), r, self.color, -1, cv2.LINE_AA)
        elif self.shape == "square":
            s = self.ball_params["square"]["side"]
            top_left = (pos[0] - s // 2, pos[1] - s // 2)
            bottom_right = (pos[0] + s // 2, pos[1] + s // 2)
            cv2.rectangle(frame, top_left, bottom_right, self.color, -1)
        elif self.shape == "rectangle":
            w = self.ball_params["rectangle"]["width"]
            h = self.ball_params["rectangle"]["height"]
            top_left = (pos[0] - w // 2, pos[1] - h // 2)
            bottom_right = (pos[0] + w // 2, pos[1] + h // 2)
            cv2.rectangle(frame, top_left, bottom_right, self.color, -1)
        elif self.shape == "triangle":
            s = self.ball_params["triangle"]["side"]
            pt1 = (pos[0], pos[1] - int(s / np.sqrt(3)))
            pt2 = (pos[0] - s // 2, pos[1] + int(s / (2 * np.sqrt(3))))
            pt3 = (pos[0] + s // 2, pos[1] + int(s / (2 * np.sqrt(3))))
            pts = np.array([pt1, pt2, pt3], np.int32)
            cv2.fillPoly(frame, [pts], self.color)