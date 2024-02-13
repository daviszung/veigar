import pygame
from typing import List, Any
from scripts.utils import load_images
from scripts.animation import Animation


class Enemy:
    def __init__(self, id: int, type: str, max_hp: int, rect: pygame.Rect):
        self.id = id
        self.type = type
        self.animations = {
            "imp": {
                "idle": Animation(load_images("frames/imp/idle"), 8, loop = True),
                "run": Animation(load_images("frames/imp/run"), 4, loop = True),
            }
        }
        self.action = "run"
        self.animation_stage = 0
        self.max_hp = max_hp
        self.hp = max_hp
        self.rect = rect
        self.despawn_mark = False
        self.flip = False
        self.y_velocity = 0
        self.x_movement = 0

    def update(self):
        self.animations[self.type][self.action].update()
    
    def move(self, x_movement: int, other_enemies: List[Any]):
        self.rect.x += x_movement

        for enemy in other_enemies:
            if enemy != self and self.rect.colliderect(enemy.rect):
                self.rect.x -= x_movement
