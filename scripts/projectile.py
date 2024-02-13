import pygame


class Projectile:
    def __init__(
        self,
        loc: list[float],
        velocity: list[float],
    ):
        self.surf = pygame.Surface((20, 20))
        self.rect = pygame.Rect((loc[0], loc[1]), (8, 8))
        self.velocity = velocity
        self.color = pygame.Color(115, 62, 239)
        self.radius = 3
        self.despawn_mark = False
