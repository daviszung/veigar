import pygame

from scripts.utils import load_images
from scripts.animation import Animation

class Player:
    def __init__(self):
        player_animations = {
            "idle": Animation(load_images("mage/Idle"), 8, True),
            "run": Animation(load_images("mage/Run"), 4, True),
            "falling": Animation(load_images("mage/Falling"), loop = True),
            "rising": Animation(load_images("mage/Rising"), loop = True),
            "attack": Animation(load_images("mage/Attack/StaffWood"), 6, False),
            "hit": Animation(load_images("mage/Hit"), 50, loop = False),
            "dying": Animation(load_images("mage/Dying"), 16, False),
            "dead": Animation(load_images("mage/Dead"), loop = False)
        }
        self.images = player_animations
        self.size = 16
        self.hitbox = pygame.Rect(50, 144, self.size, self.size)
        self.terminal_velocity = 5
        self.y_velocity: float = 0
        self.airtime = 0
        self.invincibility_frames = 0
        self.flip = False
        self.action = "idle"
        self.controls_lock = False

    def update(self):
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        
        self.images[self.action].update()

        # idle after an attack
        if self.action == "attack" and self.images[self.action].done:
            self.action = "idle"

        self.y_velocity = min(self.terminal_velocity, self.y_velocity + 0.2)

