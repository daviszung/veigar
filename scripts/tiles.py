import pygame
from typing import Dict, List, Tuple

tile_size = 16

class Tilemap():
    def __init__(self, map: Dict[str, List[Tuple[int, int]]] , tile: pygame.SurfaceType):
        self.map = map
        self.tile = tile


    def render(self, surf: pygame.SurfaceType):
        for i in self.map:
            for coords in self.map[i]:
                surf.blit(self.tile, (coords[0] * tile_size, coords[1] * tile_size))

        return surf
