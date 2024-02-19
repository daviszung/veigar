import pygame


class Item():
    def __init__(self, image: pygame.Surface, kind: str, rect: pygame.Rect, duration: float):
        self.image = image
        self.kind = kind
        self.rect = rect
        self.duration = duration
        self.despawn_mark = False
    
    def update(self):
        self.duration -= 0.1
        if self.duration <= 0:
            self.despawn_mark = True