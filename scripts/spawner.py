import pygame
import random
from typing import List

from scripts.enemy import Enemy

enemy_sizes = {
     "imp": (12, 16),
}

class Spawner():
    def __init__(self):
        self.timer = 0
        self.enemy_id_count = 1

    def tick(self, enemies: List[Enemy]):
        self.timer += 1
        if self.timer % 60 and random.randint(1, 40 * (len(enemies) + 1)) == 1:
            print(len(enemies), self.enemy_id_count)
            if len(enemies) < 4:
                self.spawn_enemy("imp", 5, enemies)



    def spawn_enemy(self, type: str, hp: int, enemies: List[Enemy]):
        enemy_location = (random.randint(0, 304), 0)
        enemy_rect = pygame.Rect(enemy_location, enemy_sizes[type])
        enemies.append(Enemy(self.enemy_id_count, type, hp, enemy_rect))
        self.enemy_id_count += 1
