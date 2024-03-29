import pygame
from typing import List, Any
from scripts.utils import load_images
from scripts.animation import Animation

enemy_offset: dict[str, List[int]] = {
    "imp": [-3, -4],
    "mawface": [-5, -6]
}

item_drop_chance = {
    "imp": 9,
    "mawface": 1
}

hp_bar_size = {
    "imp": 16,
    "mawface": 32
}

malice_reward = {
    "imp": 1,
    "mawface": 5
}


class Enemy:
    def __init__(self, id: int, type: str, max_hp: int, rect: pygame.Rect):
        self.id = id
        self.type = type
        self.animations = {
            "imp": {
                "idle": Animation(load_images("frames/imp/idle"), 8, loop = True),
                "run": Animation(load_images("frames/imp/run"), 4, loop = True),
            },
            "mawface": {
                "idle": Animation(load_images("frames/mawface/idle"), 8, loop = True),
                "run": Animation(load_images("frames/mawface/run"), 6, loop = True),
            }
        }
        self.action = "run"
        self.animation_stage = 0
        self.max_hp = max_hp
        self.hp = max_hp
        self.rect = rect
        self.offset = enemy_offset[type]
        self.despawn_mark = False
        self.flip = False
        self.terminal_velocity = 1
        self.y_velocity = 0
        self.x_movement = 0
        self.drop_chance = item_drop_chance[type]
        self.hp_bar = pygame.Surface((hp_bar_size[type], 1))
        self.malice_reward = malice_reward[type]


    def update(self):
        self.animations[self.type][self.action].update()
    
    def move(self, x_movement: int, other_enemies: List[Any], tiles: List[pygame.Rect]):
        collisions: List[pygame.Rect] = []
        self.rect.x += x_movement

        for enemy in other_enemies:
            if enemy != self and self.rect.colliderect(enemy.rect):
                self.rect.x -= x_movement
            
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

        for enemy in other_enemies:
            if enemy != self and self.rect.colliderect(enemy.rect):
                self.rect.y -= self.y_velocity

        for tile in tiles:
            if self.rect.colliderect(tile):
                collisions.append(tile)
    
        for tile in collisions:
            if self.y_velocity > 0:
                self.rect.bottom = tile.top
                self.y_velocity = 0
            elif self.y_velocity < 0:
                self.rect.top = tile.bottom

