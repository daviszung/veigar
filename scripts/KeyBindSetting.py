import pygame
from scripts.utils import center_rect

class KeyBindSetting():
    def __init__(self, identifier: int, rect: pygame.Rect, key: int, settings_name: str):
        self.id = identifier
        self.surf = pygame.Surface((36, 14))
        self.rect = rect
        self.key = key
        self.settings_name = settings_name

        font = pygame.Font("./assets/fonts/KodeMonoVariableWeight.ttf", 10)
        img = font.render(pygame.key.name(self.key), False, pygame.Color(255, 255, 255))
        self.surf.blit(img, center_rect(img.get_rect(), self.surf.get_rect()))
    