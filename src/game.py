import cv2
import pygame
import logging
import random
import numpy as np
from typing import Optional, List, Tuple

from src.settings import *
from src.components.ball import Ball
from src.components.target import Target
from src.components.obstacle import Obstacle
from src.components.powerup import PowerUp
from src.components.particle_effect import ParticleEffect
from src.utils.red_object_detector import RedObjectDetector

class Game:
    """
    Main game controller class that manages the game loop, state, and rendering.
    """
    def __init__(self, **sound_paths):
        self._setup_logging()
        self._init_pygame_mixer()
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        
        self.detector = RedObjectDetector()
        
        self.score = 0
        self.hearts = 15
        self.level = 1
        self.combo_counter = 0
        self.combo_multiplier = 1
        self.shield_active = False
        self.shield_timer = 0
        self.frame_counter = 0
        self.last_heart_threshold = 0
        
        self.effects: List[ParticleEffect] = []
        self.effect_colors: List[Tuple[int,int,int]] = []
        
        self._reset_game_elements()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
        self.logger = logging.getLogger(__name__)

    def _init_pygame_mixer(self) -> dict:
        try:
            pygame.mixer.init()
            self.logger.info("Pygame mixer initialized successfully.")
        except pygame.error as e:
            self.logger.error(f"Pygame mixer could not be initialized: {e}")
           

    def _play_sound(self, name: str):
        pygame.mixer.Sound.play(pygame.mixer.Sound(SOUNDS[name])) if name in SOUNDS else self.logger.warning(f"Sound '{name}' is not available or failed to load.")
            
    # In src/game.py

    def _reset_game_elements(self):
        self.ball = Ball(CANVAS_SIZE, BALL_PARAMS, SHAPES, NUM_PARTICLES)
        self.targets = Target.create_targets(CANVAS_SIZE, TARGET_PARAMS, SHAPES)
        self.obstacles = [Obstacle(CANVAS_SIZE, self.level) for _ in range(3)]
        self.powerups: List[PowerUp] = []

        # This loop ensures the ball doesn't spawn inside an obstacle.
        while True:
            # Create a new ball at a random position
            self.ball = Ball(CANVAS_SIZE, BALL_PARAMS, SHAPES, NUM_PARTICLES)
            
            # Check if the new ball's starting position is colliding with any obstacle
            is_colliding = any(obs.collides_with(self.ball) for obs in self.obstacles)
            
            # If it's not colliding, we found a safe spot, so we can exit the loop
            if not is_colliding:
                break

    def run(self):
        """Main game loop."""
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            self.frame_counter += 1

            measurement = self.detector.detect(frame)
            self._update_game_state(measurement)
            self._check_collisions_and_events()
            self._render(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if self.hearts <= 0:
                self._game_over_screen(frame)
                break

        self._cleanup()

    def _update_game_state(self, measurement: Optional[np.ndarray]):
        self.ball.update(measurement, MOTION_NOISE, ACCELERATION_NOISE)
        for obs in self.obstacles:
            obs.update()

        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False

        if self.frame_counter % 500 == 0 and random.random() < 0.5:
            self.powerups.append(PowerUp(CANVAS_SIZE))
            
    def _check_collisions_and_events(self):
        ball_pos = self.ball.get_position()
        event_triggered = False

        # Power-up collision
        for powerup in self.powerups[:]:
            if np.linalg.norm(ball_pos - powerup.position) < (self.ball.get_radius() + powerup.radius):
                self.shield_active = True
                self.shield_timer = powerup.duration
                self.powerups.remove(powerup)
                self._play_sound("powerup")
                self.effects.append(ParticleEffect(powerup.position))
                self.effect_colors.append(COLORS["effect_powerup"])
                
        # Obstacle collision
        for obs in self.obstacles:
            if obs.collides_with(self.ball):
                self._handle_penalty(ball_pos)
                event_triggered = True
                break
        if event_triggered: return

        # Target collision
        for target in self.targets:
            if target.point_inside(ball_pos):
                if self.ball.shape == target.shape:
                    self._handle_success(target.position)
                else:
                    self._handle_penalty(target.position)
                event_triggered = True
                break
        
        if event_triggered:
            self._check_level_up()
            self._reset_game_elements()
            
    def _handle_success(self, position: np.ndarray):
        self.combo_counter += 1
        self.combo_multiplier = 1 + (self.combo_counter // 3)
        self.score += self.combo_multiplier
        self._play_sound("score")
        if self.combo_counter > 0 and self.combo_counter % 3 == 0:
             self._play_sound("combo")
        self.effects.append(ParticleEffect(position))
        self.effect_colors.append(COLORS["effect_success"])
        
    def _handle_penalty(self, position: np.ndarray):
        if not self.shield_active:
            self.hearts -= 1
            self._play_sound("penalty")
        self.shield_active = False
        self.combo_counter = 0
        self.combo_multiplier = 1
        self.effects.append(ParticleEffect(position))
        self.effect_colors.append(COLORS["effect_fail"])
        
    def _check_level_up(self):
        new_level = self.score // 5 + 1
        if new_level > self.level:
            self.level = new_level
            self._play_sound("levelup")
            
    def _render(self, frame: np.ndarray):
        for target in self.targets: target.draw(frame)
        self.ball.draw(frame)
        for obs in self.obstacles: obs.draw(frame)
        for powerup in self.powerups: powerup.draw(frame)
        
        active_effects = []
        active_colors = []
        # Iterate through the effects and their corresponding colors
        for i, effect in enumerate(self.effects):
            # update_and_draw returns True if the effect is finished
            is_finished = effect.update_and_draw(frame, self.effect_colors[i])
            
            # Keep the effect and its color only if it's not finished
            if not is_finished:
                active_effects.append(effect)
                active_colors.append(self.effect_colors[i])

        # Replace the old lists with the new lists of active effects
        self.effects = active_effects
        self.effect_colors = active_colors
        
        self._draw_ui(frame)
        cv2.imshow("Shape Matching Game", frame)

    def _draw_ui(self, frame: np.ndarray):
        cv2.putText(frame, f"Score: {self.score}", (50, 50), UI_TEXT_FONT, UI_TEXT_SCALE, UI_COLORS["score"], UI_TEXT_THICKNESS)
        cv2.putText(frame, f"Hearts: {self.hearts}", (50, 100), UI_TEXT_FONT, UI_TEXT_SCALE, UI_COLORS["hearts"], UI_TEXT_THICKNESS)
        cv2.putText(frame, f"Level: {self.level}", (50, 150), UI_TEXT_FONT, UI_TEXT_SCALE, UI_COLORS["level"], UI_TEXT_THICKNESS)
        cv2.putText(frame, f"Combo: x{self.combo_multiplier}", (50, 200), UI_TEXT_FONT, UI_TEXT_SCALE, UI_COLORS["combo"], UI_TEXT_THICKNESS)
        if self.shield_active:
            cv2.putText(frame, "Shield Active", (50, 250), UI_TEXT_FONT, UI_TEXT_SCALE, UI_COLORS["shield"], UI_TEXT_THICKNESS)
            
    def _game_over_screen(self, frame: np.ndarray):
        text = "GAME OVER"
        text_size = cv2.getTextSize(text, UI_TEXT_FONT, 2, 4)[0]
        text_x = (WIDTH - text_size[0]) // 2
        text_y = (HEIGHT + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), UI_TEXT_FONT, 2, UI_COLORS["game_over"], 4)
        cv2.imshow("Shape Matching Game", frame)
        cv2.waitKey(3000)

    def _cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        pygame.mixer.quit()