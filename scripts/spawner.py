import pygame
import math
import random
from typing import List

from scripts.enemy import Enemy

enemy_sizes = {
    "imp": (10, 12),
    "mawface": (20, 30)
}


class Spawner:
    def __init__(self):
        self.timer = 0
        self.enemy_id_count = 1

    def tick(self, enemies: List[Enemy], malice: int):
        max_enemies = 1 + int(math.log(malice + 1, 2))
        self.timer += 1
        if len(enemies) == 0 and self.timer % 60 == 0:
            self.spawn_enemy("mawface", 50, enemies)
            return

        if (
            len(enemies) < max_enemies
            and self.timer % 60 == 0
            and random.randint(1, max(4, 30 - malice)) == 1
        ):
            self.spawn_enemy("mawface", 50, enemies)


    def spawn_enemy(self, type: str, hp: int, enemies: List[Enemy]):
        enemy_location = (random.randint(0, 304), 0)
        enemy_rect = pygame.Rect(enemy_location, enemy_sizes[type])
        enemies.append(Enemy(self.enemy_id_count, type, hp, enemy_rect))
        self.enemy_id_count += 1
