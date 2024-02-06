import pygame
from scripts.utils import load_images
from scripts.animation import Animation


class Enemy:
    def __init__(self, type: str, max_hp: int, rect: pygame.Rect):
        self.type = type
        self.animations = {
            "imp": {
                "idle": Animation(load_images("frames/imp/idle"), 8, loop = True),
                "run": Animation(load_images("frames/imp/run"), 4, loop = True),
            }
        }
        self.action = "idle"
        self.animation_stage = 0
        self.max_hp = max_hp
        self.hp = max_hp
        self.rect = rect
        self.despawn_mark = False

    def update(self):
        self.animations[self.type][self.action].update()

