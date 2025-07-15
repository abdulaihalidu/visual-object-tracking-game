import cv2
import numpy as np
import random
from typing import Tuple, List, Dict

from src.settings import COLORS

class Target:
    """
    Represents a target zone on the canvas, displayed as an outline of a shape.
    """
    def __init__(self, shape: str, position: np.ndarray, canvas_size: Tuple[int, int, int], target_params: Dict):
        self.shape = shape
        self.position = position
        self.canvas_size = canvas_size
        self.target_params = target_params
        self.color = COLORS["target_outline"]
        self.thickness = 3

    @staticmethod
    def create_targets(canvas_size: Tuple, target_params: Dict, shapes: List[str]) -> List['Target']:
        targets = []
        shapes_copy = random.sample(shapes, len(shapes))
        corners = ["top_left", "top_right", "bottom_left", "bottom_right"]
        for i, corner in enumerate(corners):
            shape = shapes_copy[i]
            margin = Target.get_margin(shape, target_params)
            if corner == "top_left":
                x = random.randint(margin, margin + 50)
                y = random.randint(margin, margin + 50)
            elif corner == "top_right":
                x = random.randint(canvas_size[1] - margin - 50, canvas_size[1] - margin)
                y = random.randint(margin, margin + 50)
            elif corner == "bottom_left":
                x = random.randint(margin, margin + 50)
                y = random.randint(canvas_size[0] - margin - 50, canvas_size[0] - margin)
            else: # bottom_right
                x = random.randint(canvas_size[1] - margin - 50, canvas_size[1] - margin)
                y = random.randint(canvas_size[0] - margin - 50, canvas_size[0] - margin)
            
            position = np.array([x, y])
            targets.append(Target(shape, position, canvas_size, target_params))
        return targets

    @staticmethod
    def get_margin(shape: str, target_params: Dict) -> int:
        if shape == "circle": return target_params["circle"]["radius"]
        if shape == "square": return target_params["square"]["side"] // 2
        if shape == "rectangle": return max(target_params["rectangle"]["width"], target_params["rectangle"]["height"]) // 2
        if shape == "triangle": return target_params["triangle"]["side"]
        return 50

    def draw(self, frame: np.ndarray):
        pos = self.position.astype(int)
        if self.shape == "circle":
            r = self.target_params["circle"]["radius"]
            cv2.circle(frame, tuple(pos), r, self.color, self.thickness, cv2.LINE_AA)
        elif self.shape == "square":
            s = self.target_params["square"]["side"]
            top_left = (pos[0] - s // 2, pos[1] - s // 2)
            bottom_right = (pos[0] + s // 2, pos[1] + s // 2)
            cv2.rectangle(frame, top_left, bottom_right, self.color, self.thickness)
        elif self.shape == "rectangle":
            w = self.target_params["rectangle"]["width"]
            h = self.target_params["rectangle"]["height"]
            top_left = (pos[0] - w // 2, pos[1] - h // 2)
            bottom_right = (pos[0] + w // 2, pos[1] + h // 2)
            cv2.rectangle(frame, top_left, bottom_right, self.color, self.thickness)
        elif self.shape == "triangle":
            s = self.target_params["triangle"]["side"]
            pt1 = (pos[0], pos[1] - int(s / np.sqrt(3)))
            pt2 = (pos[0] - s // 2, pos[1] + int(s / (2 * np.sqrt(3))))
            pt3 = (pos[0] + s // 2, pos[1] + int(s / (2 * np.sqrt(3))))
            pts = np.array([pt1, pt2, pt3], np.int32)
            cv2.polylines(frame, [pts], isClosed=True, color=self.color, thickness=self.thickness)

    def point_inside(self, point: np.ndarray) -> bool:
        pos = self.position
        if self.shape == "circle":
            r = self.target_params["circle"]["radius"]
            return np.linalg.norm(point - pos) < r
        elif self.shape == "square":
            s = self.target_params["square"]["side"]
            return (abs(point[0] - pos[0]) < s / 2) and (abs(point[1] - pos[1]) < s / 2)
        elif self.shape == "rectangle":
            w = self.target_params["rectangle"]["width"]
            h = self.target_params["rectangle"]["height"]
            return (abs(point[0] - pos[0]) < w / 2) and (abs(point[1] - pos[1]) < h / 2)
        elif self.shape == "triangle":
            s = self.target_params["triangle"]["side"]
            pt1 = (pos[0], pos[1] - int(s / np.sqrt(3)))
            pt2 = (pos[0] - s // 2, pos[1] + int(s / (2 * np.sqrt(3))))
            pt3 = (pos[0] + s // 2, pos[1] + int(s / (2 * np.sqrt(3))))
            pts = np.array([pt1, pt2, pt3], np.int32)
            return cv2.pointPolygonTest(pts, (int(point[0]), int(point[1])), False) >= 0
        return False