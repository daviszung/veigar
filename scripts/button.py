import pygame

from typing import Callable

class Button():
    def __init__(self, name: str, callback: Callable[..., None], rect: pygame.Rect, text: str):
        self.name = name
        self.callback = callback
        self.rect = rect
        self.text = text
        self.text_color = pygame.Color((255, 255, 255))
    
