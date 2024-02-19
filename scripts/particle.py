import pygame

from typing import List


class Particle:
    def __init__(self, loc: List[float], velocity: List[float], timer: float, color: pygame.Color):
        self.loc = loc
        self.velocity = velocity
        self.timer = timer
        self.despawn_mark = False
        self.color = color

    def update(self):
        self.loc[0] += self.velocity[0] / 2
        self.loc[1] += self.velocity[1] / 2
        self.velocity[1] += 0.07

        self.timer -= 0.1
        if self.timer <= 0:
            self.despawn_mark = True
