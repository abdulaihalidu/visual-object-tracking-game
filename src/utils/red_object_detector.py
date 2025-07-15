import cv2
import numpy as np
from typing import Optional, Tuple

from src.settings import RED_LOWER1, RED_UPPER1, RED_LOWER2, RED_UPPER2

class RedObjectDetector:
    """
    Detects a moving red object in a video frame using background subtraction and color segmentation.
    """
    def __init__(self, history: int = 100, var_threshold: int = 16, detect_shadows: bool = True):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history, varThreshold=var_threshold, detectShadows=detect_shadows
        )

    def detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Processes a frame to find the tip of the largest moving red object.
        """
        fg_mask = self.bg_subtractor.apply(frame)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask1 = cv2.inRange(hsv_frame, RED_LOWER1, RED_UPPER1)
        mask2 = cv2.inRange(hsv_frame, RED_LOWER2, RED_UPPER2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        combined_mask = cv2.bitwise_and(red_mask, red_mask, mask=fg_mask)
        combined_mask = cv2.erode(combined_mask, None, iterations=2)
        combined_mask = cv2.dilate(combined_mask, None, iterations=2)
        combined_mask = cv2.GaussianBlur(combined_mask, (7, 7), 0)

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)

        if M["m00"] == 0:
            return None
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        hull = cv2.convexHull(largest_contour)
        
        farthest_point = None
        max_distance = 0
        
        for point in hull:
            pt = point[0]
            distance = np.linalg.norm(np.array([cx, cy]) - pt)
            if distance > max_distance:
                max_distance = distance
                farthest_point = pt
                
        return np.array(farthest_point) if farthest_point is not None else None