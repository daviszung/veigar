import pygame


class Projectile:
    def __init__(
        self,
        surf: pygame.Surface,
        loc: list[float],
        velocity: list[float],
        radius: float,
        color: pygame.Color
    ):
        self.surf = surf
        self.rect = pygame.Rect((loc[0], loc[1]), (8, 8))
        self.velocity = velocity
        self.color = color
        self.radius = radius
        self.despawn_mark = False
