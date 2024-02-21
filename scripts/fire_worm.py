import pygame

from typing import List
from scripts.animation import Animation
from scripts.utils import load_img


def extract_image(path: str, rects: List[pygame.Rect]):
    base = load_img(path)
    all_frames: List[pygame.Surface] = []
    for r in rects:
        all_frames.append(base.subsurface(r))
    return all_frames


class FireWorm:

    def __init__(self):
        self.max_hp = 2500
        self.hp = self.max_hp
        self.rect = pygame.Rect(150, 60, 54, 34)
        self.offset = [-16, -24]
        self.animations = {
            "idle": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Idle.png",
                    [
                        pygame.Rect(0, 0, 74, 58),
                        pygame.Rect(90, 0, 74, 58),
                        pygame.Rect(180, 0, 74, 58),
                        pygame.Rect(270, 0, 74, 58),
                        pygame.Rect(360, 0, 74, 58),
                        pygame.Rect(450, 0, 74, 58),
                        pygame.Rect(540, 0, 74, 58),
                        pygame.Rect(630, 0, 74, 58),
                        pygame.Rect(720, 0, 74, 58),
                    ],
                ),
                img_dur=6,
                loop=True
            ),

            "walk": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Walk.png",
                    [
                        pygame.Rect(0, 0, 74, 58),
                        pygame.Rect(90, 0, 74, 58),
                        pygame.Rect(180, 0, 74, 58),
                        pygame.Rect(270, 0, 74, 58),
                        pygame.Rect(360, 0, 74, 58),
                        pygame.Rect(450, 0, 74, 58),
                        pygame.Rect(540, 0, 74, 58),
                        pygame.Rect(630, 0, 74, 58),
                        pygame.Rect(720, 0, 74, 58),
                    ],
                ),
                img_dur=6,
                loop=True
            ),

            "attack": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Attack.png",
                    [
                        pygame.Rect(0, 0, 74, 58),
                        pygame.Rect(90, 0, 74, 58),
                        pygame.Rect(180, 0, 74, 58),
                        pygame.Rect(270, 0, 74, 58),
                        pygame.Rect(360, 0, 74, 58),
                        pygame.Rect(450, 0, 74, 58),
                        pygame.Rect(540, 0, 74, 58),
                        pygame.Rect(630, 0, 74, 58),
                        pygame.Rect(720, 0, 74, 58),
                        pygame.Rect(810, 0, 74, 58),
                        pygame.Rect(900, 0, 74, 58),
                        pygame.Rect(990, 0, 74, 58),
                        pygame.Rect(1080, 0, 74, 58),
                        pygame.Rect(1170, 0, 74, 58),
                        pygame.Rect(1260, 0, 74, 58),
                        pygame.Rect(1350, 0, 74, 58),
                    ],
                ),
                img_dur=5,
                loop=False
            ),

            "death": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Death.png",
                    [
                        pygame.Rect(0, 0, 74, 58),
                        pygame.Rect(90, 0, 74, 58),
                        pygame.Rect(180, 0, 74, 58),
                        pygame.Rect(270, 0, 74, 58),
                        pygame.Rect(360, 0, 74, 58),
                        pygame.Rect(450, 0, 74, 58),
                        pygame.Rect(540, 0, 74, 58),
                        pygame.Rect(630, 0, 74, 58),
                    ],
                ),
                img_dur=10,
                loop=False
            )
        }
        self.action = "death"
        self.flip = False

    def update(self):
        self.animations[self.action].update()
