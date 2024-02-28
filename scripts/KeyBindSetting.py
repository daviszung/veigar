import pygame
from scripts.utils import center_rect

class KeyBindSetting():
    def __init__(self, rect: pygame.Rect, key: int):
        self.surf = pygame.Surface((36, 14))
        self.rect = rect
        self.key = key

        font = pygame.Font(None, 16)
        img = font.render(pygame.key.name(self.key), False, pygame.Color(255, 255, 255))
        self.surf.blit(img, center_rect(img.get_rect(), self.surf.get_rect()))
    