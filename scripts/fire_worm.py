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
        self.offset = [0, -24]
        self.animations = {
            "idle": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Idle.png",
                    [
                        pygame.Rect(16, 0, 54, 58),
                        pygame.Rect(106, 0, 54, 58),
                        pygame.Rect(196, 0, 54, 58),
                        pygame.Rect(286, 0, 54, 58),
                        pygame.Rect(376, 0, 54, 58),
                        pygame.Rect(466, 0, 54, 58),
                        pygame.Rect(556, 0, 54, 58),
                        pygame.Rect(646, 0, 54, 58),
                        pygame.Rect(736, 0, 54, 58),
                    ],
                ),
                img_dur=6,
                loop=True
            ),
            "walk": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Walk.png",
                    [
                        pygame.Rect(16, 0, 54, 58),
                        pygame.Rect(106, 0, 54, 58),
                        pygame.Rect(196, 0, 54, 58),
                        pygame.Rect(286, 0, 54, 58),
                        pygame.Rect(376, 0, 54, 58),
                        pygame.Rect(466, 0, 54, 58),
                        pygame.Rect(556, 0, 54, 58),
                        pygame.Rect(646, 0, 54, 58),
                        pygame.Rect(736, 0, 54, 58),
                    ],
                ),
                img_dur=6,
                loop=True
            ),
            "attack": Animation(
                extract_image(
                    "fireworm/Sprites/Worm/Attack.png",
                    [
                        pygame.Rect(16, 0, 54, 58),
                        pygame.Rect(106, 0, 54, 58),
                        pygame.Rect(196, 0, 54, 58),
                        pygame.Rect(286, 0, 54, 58),
                        pygame.Rect(376, 0, 54, 58),
                        pygame.Rect(466, 0, 54, 58),
                        pygame.Rect(556, 0, 54, 58),
                        pygame.Rect(646, 0, 54, 58),
                        pygame.Rect(736, 0, 54, 58),
                        pygame.Rect(826, 0, 54, 58),
                        pygame.Rect(916, 0, 54, 58),
                        pygame.Rect(1006, 0, 54, 58),
                        pygame.Rect(1096, 0, 54, 58),
                        pygame.Rect(1186, 0, 54, 58),
                        pygame.Rect(1276, 0, 54, 58),
                        pygame.Rect(1366, 0, 54, 58),
                    ],
                ),
                img_dur=5,
                loop=True
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
            ),
        }
        self.action = "attack"
        self.flip = False

    def update(self):
        self.animations[self.action].update()
