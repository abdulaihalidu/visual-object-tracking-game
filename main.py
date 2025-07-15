import sys
import os
from src.game import Game
from src.settings import SOUNDS

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

def main():
    """
    Initializes and runs the game.
    """
    game = Game(
        score_sound_path=SOUNDS["score"],
        penalty_sound_path=SOUNDS["penalty"],
        levelup_sound_path=SOUNDS["levelup"],
        powerup_sound_path=SOUNDS["powerup"],
        combo_sound_path=SOUNDS["combo"]
    )
    game.run()

if __name__ == "__main__":
    main()