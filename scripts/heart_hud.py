import pygame
from typing import Dict


class HeartHud:
    def __init__(self, images: Dict[str, pygame.Surface]):
        self.max_hearts = 3
        self.hearts = 3
        self.images = images
        self.surf = pygame.Surface((46, 12), pygame.SRCALPHA, 32)

    def update(self, heart_modifier: int):
        self.hearts = min(self.max_hearts, self.hearts + heart_modifier)
        for i in range(self.max_hearts):
            if self.hearts >= i + 1:
                self.surf.blit(self.images["heart"], (i * 16, 0))
            else:
                self.surf.blit(self.images["empty_heart"], (i * 16, 0))
