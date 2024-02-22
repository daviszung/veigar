import pygame

from scripts.animation import Animation
from scripts.utils import extract_image
from typing import List

class FireBall():
    def __init__(self, loc: List[int], velocity: List[int], flip: bool):
        self.rect = pygame.Rect(loc[0], loc[1], 16, 14)
        self.velocity = velocity
        self.despawn_mark = False
        self.flip = flip
        self.action = "move"
        self.animations = {
            "move": Animation(extract_image("fireworm/Sprites/fireball/Move.png", [pygame.Rect(16, 16, 16, 16), pygame.Rect(62, 16, 16, 16),pygame.Rect(108, 16, 16, 16), pygame.Rect(154, 16, 16, 16), pygame.Rect(200, 16, 16, 16), pygame.Rect(246, 16, 16, 16)])),
        }

    def update(self):
        self.animations[self.action].update()