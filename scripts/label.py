import pygame

class Label():
    def __init__(self, name: str, rect: pygame.Rect, text: str):
        self.name = name
        self.rect = rect
        self.text = text
        # self.text_color = pygame.Color((255, 255, 255))
    
