import pygame
from typing import Dict, List, Tuple


class Tilemap():
    def __init__(self, map: Dict[str, List[Tuple[int, int]]] , tile: pygame.SurfaceType):
        self.map = map
        self.tile = tile
        self.tile_size = 16


    def render(self, surf: pygame.SurfaceType):
        for i in self.map:
            for coords in self.map[i]:
                surf.blit(self.tile, (coords[0] * self.tile_size, coords[1] * self.tile_size))