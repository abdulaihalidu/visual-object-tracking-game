import cv2
import numpy as np
import random
from typing import Tuple, List, Dict

class ParticleEffect:
    """
    Creates a particle explosion effect for visual feedback on game events.
    """
    def __init__(self, position: np.ndarray, num_particles: int = 50):
        self.particles: List[Dict] = []
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(2, 7)
            velocity = np.array([speed * np.cos(angle), speed * np.sin(angle)], dtype=float)
            self.particles.append({
                "pos": position.astype(float).copy(),
                "vel": velocity,
                "lifetime": random.randint(20, 40)
            })

    def update_and_draw(self, frame: np.ndarray, color: Tuple[int, int, int]):
        """Updates particle positions, reduces their lifetime, and draws them."""
        for p in self.particles:
            p["pos"] += p["vel"]
            p["lifetime"] -= 1
            if p["lifetime"] > 0:
                cv2.circle(frame, (int(p["pos"][0]), int(p["pos"][1])), 2, color, -1)
        
        self.particles = [p for p in self.particles if p["lifetime"] > 0]
        return len(self.particles) == 0