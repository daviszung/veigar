import pygame
import random

from typing import List
from scripts.animation import Animation
from scripts.utils import extract_image

class FireWorm:
    def __init__(self, loc: List[int]):
        self.max_hp = 25
        self.hp = self.max_hp
        self.y_velocity = 0
        self.terminal_velocity = 3
        self.rect = pygame.Rect(loc[0], loc[1], 54, 30)
        self.offset = [0, -28]
        self.animations = {
            "idle": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Idle.png",
                    [
                        pygame.Rect(16, 0, 54, 58),
                        pygame.Rect(106, 0, 54, 58),
                        pygame.Rect(196, 0, 54, 58),
                        pygame.Rect(286, 0, 54, 58),
                        pygame.Rect(376, 0, 54, 58),
                        pygame.Rect(466, 0, 54, 58),
                        pygame.Rect(556, 0, 54, 58),
                        pygame.Rect(646, 0, 54, 58),
                        pygame.Rect(736, 0, 54, 58),
                    ],
                ),
                img_dur=6,
                loop=False
            ),
            "walk": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Walk.png",
                    [
                        pygame.Rect(16, 0, 54, 58),
                        pygame.Rect(106, 0, 54, 58),
                        pygame.Rect(196, 0, 54, 58),
                        pygame.Rect(286, 0, 54, 58),
                        pygame.Rect(376, 0, 54, 58),
                        pygame.Rect(466, 0, 54, 58),
                        pygame.Rect(556, 0, 54, 58),
                        pygame.Rect(646, 0, 54, 58),
                        pygame.Rect(736, 0, 54, 58),
                    ],
                ),
                img_dur=6,
                loop=False
            ),
            "attack": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Attack.png",
                    [
                        pygame.Rect(16, 0, 54, 58),
                        pygame.Rect(106, 0, 54, 58),
                        pygame.Rect(196, 0, 54, 58),
                        pygame.Rect(286, 0, 54, 58),
                        pygame.Rect(376, 0, 54, 58),
                        pygame.Rect(466, 0, 54, 58),
                        pygame.Rect(556, 0, 54, 58),
                        pygame.Rect(646, 0, 54, 58),
                        pygame.Rect(736, 0, 54, 58),
                        pygame.Rect(826, 0, 54, 58),
                        pygame.Rect(916, 0, 54, 58),
                        pygame.Rect(1006, 0, 54, 58),
                        pygame.Rect(1096, 0, 54, 58),
                        pygame.Rect(1186, 0, 54, 58),
                        pygame.Rect(1276, 0, 54, 58),
                        pygame.Rect(1366, 0, 54, 58),
                    ],
                ),
                img_dur=5,
                loop=False
            ),
            "death": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Death.png",
                    [
                        pygame.Rect(0, 0, 74, 58),
                        pygame.Rect(90, 0, 74, 58),
                        pygame.Rect(180, 0, 74, 58),
                        pygame.Rect(270, 0, 74, 58),
                        pygame.Rect(360, 0, 74, 58),
                        pygame.Rect(450, 0, 74, 58),
                        pygame.Rect(540, 0, 74, 58),
                        pygame.Rect(630, 0, 74, 58),
                    ],
                ),
                img_dur=20,
                loop=False
            ),
        }
        self.action = "idle"
        self.flip = False
        self.despawn_mark = False

    def update(self):
        self.animations[self.action].update()
        if self.action != "death":
            self.decide_action()

        if self.action == "death" and self.animations["death"].done:
            self.despawn_mark = True
    
    def walk(self):
        self.action = "walk"
        self.animations["walk"] = self.animations["walk"].copy()

    def move(self, x_movement: int, tiles: List[pygame.Rect]):
        collisions: List[pygame.Rect] = []
        self.rect.x += x_movement

        for tile in tiles:
            if self.rect.colliderect(tile):
                collisions.append(tile)
        
    
        for tile in collisions:
            if x_movement > 0:
                self.rect.right = tile.left
            elif x_movement < 0:
                self.rect.left = tile.right

        collisions.clear()

        self.y_velocity = min(self.terminal_velocity, self.y_velocity + 0.1)

        self.rect.y += self.y_velocity

        for tile in tiles:
            if self.rect.colliderect(tile):
                collisions.append(tile)
    
        for tile in collisions:
            if self.y_velocity > 0:
                self.rect.bottom = tile.top
                self.y_velocity = 0
            elif self.y_velocity < 0:
                self.rect.top = tile.bottom

    def attack(self):
        self.action = "attack"
        self.animations["attack"] = self.animations["attack"].copy()

    def idle(self):
        self.action = "idle"
        self.animations["idle"] = self.animations["idle"].copy()

    def decide_action(self):
        if self.animations[self.action].done:
            random.choice([self.idle, self.walk, self.attack])()

        


