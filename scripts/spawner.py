import pygame
import math
import random
from typing import List

from scripts.enemy import Enemy

enemy_sizes = {
    "imp": (10, 12),
    "mawface": (20, 30)
}

enemy_hp = {
    "imp": 5,
    "mawface": 100
}


class Spawner:
    def __init__(self):
        self.timer = 0
        self.enemy_id_count = 1

    def tick(self, enemies: List[Enemy], malice: int):
        max_enemies = 1 + int(math.log(malice + 1, 2))
        self.timer += 1
        if len(enemies) == 0 and self.timer % 60 == 0:
            self.spawn_enemy("imp", enemy_hp["imp"], enemies)
            return

        if (
            len(enemies) < max_enemies
            and self.timer % 60 == 0
            and random.randint(1, max(4, 30 - malice)) == 1
        ):
            enemy_to_spawn = ""
            if malice >= 10 and random.randint(1, 8) == 1:
                if any(e.type == "mawface" for e in enemies):
                    enemy_to_spawn = "imp"
                else:
                    enemy_to_spawn = "mawface"
            if enemy_to_spawn != "":
                self.spawn_enemy(enemy_to_spawn, enemy_hp[enemy_to_spawn], enemies)


    def spawn_enemy(self, type: str, hp: int, enemies: List[Enemy]):
        enemy_location = (random.randint(0, 304), 0)
        enemy_rect = pygame.Rect(enemy_location, enemy_sizes[type])
        enemy = Enemy(self.enemy_id_count, type, hp, enemy_rect)
        pygame.draw.rect(
            enemy.hp_bar, "red", (0, 0, (enemy.hp_bar.get_width() * enemy.hp / enemy.max_hp), 1)
        )
        enemies.append(enemy)
        self.enemy_id_count += 1
