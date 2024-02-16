import pygame
import random
from typing import List

class AudioGroup():
    def __init__(self, sounds: List[pygame.mixer.Sound]):
        self.sounds = sounds

    def play_random(self):
       selected_sound = random.choice(self.sounds)
       selected_sound.play()