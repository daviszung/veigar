import pygame
from typing import Dict


class MaliceHud:
    def __init__(self, images: Dict[str, pygame.Surface]):
        pygame.font.init()
        self.malice = 0
        self.images = images
        self.surf = pygame.Surface((48, 16), pygame.SRCALPHA, 32)
        self.font = pygame.font.Font(None, 16)
        self.font.set_point_size(12)

    def update(self, malice: int):
        self.malice = malice
        self.surf = pygame.Surface((48, 16), pygame.SRCALPHA, 32)
        self.surf.blit(self.images["malice"], (0, 0))
        text = self.font.render(str(self.malice), False, (0, 0, 0))
        self.surf.blit(text, (20, 2))
