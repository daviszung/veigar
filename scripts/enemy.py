import pygame
from typing import List, Dict

# from scripts.utils import load_img


class Enemy:
    def __init__(self, type: str, animations: Dict[str, List[pygame.Surface]], animation_change_rate: int, max_hp: int, loc: List[int]):
        self.type = type
        self.animations = animations
        self.animation_change_rate = animation_change_rate
        self.animation_timer = self.animation_change_rate
        self.current_animation = "idle"
        self.animation_stage = 0
        self.max_hp = max_hp
        self.hp = max_hp
        self.loc = loc

    def update_animation(self):
        if self.animation_timer <= 0:
            if self.animation_stage >= 3:
                self.animation_stage = 0
            else:
                self.animation_stage += 1
            self.animation_timer = self.animation_change_rate

        else:
            self.animation_timer -= 1


    def render(self, surf: pygame.Surface):
        animation = self.animations[self.current_animation][self.animation_stage]
        surf.blit(animation, (self.loc[0], self.loc[1]))

