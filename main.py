import pygame
import sys

from typing import Dict, List, Tuple

from scripts.utils import load_img
from scripts.tiles import Tilemap


map: Dict[str, List[Tuple[int, int]]] = {
    "grass": [(1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10),(11, 10),(12, 10),(13, 10),(14, 10),(15, 10),(16, 10),(17, 10), (18, 10)]
}

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("veigar")

        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.canvas_width = self.screen_width / 4
        self.canvas_height = self.screen_height / 4
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height))
        self.clock = pygame.time.Clock()

        sheet = pygame.image.load("assets/sheet.png")
        self.platform = sheet.subsurface(128, 80, 16, 16).convert()

        self.map = Tilemap(map, self.platform)

        # player
        self.player_pos = pygame.Vector2(
            self.canvas.get_width() / 2, self.canvas.get_height() / 2
        )
        self.player = load_img("Idle/Idle1.png")
        self.player.set_colorkey((0, 0, 0))
        self.player_terminal_velocity = 5
        self.playerVelocity = 0
        self.playerAirborne = True
        self.lastDirection = "right"
        self.currentAnimation = "idle"
        self.animationStage = 0

        self.player_animations = {
            "idle": [
                load_img("Idle/Idle1.png"),
                load_img("Idle/Idle2.png"),
                load_img("Idle/Idle3.png"),
                load_img("Idle/Idle4.png"),
                load_img("Idle/Idle5.png"),
                load_img("Idle/Idle6.png"),
            ],
            "run": [
                load_img("Run/Run1.png"),
                load_img("Run/Run2.png"),
                load_img("Run/Run3.png"),
                load_img("Run/Run4.png"),
                load_img("Run/Run5.png"),
                load_img("Run/Run6.png"),
            ],
            "falling": [
                load_img("Falling/Falling1.png"),
                load_img("Falling/Falling2.png"),
                load_img("Falling/Falling3.png"),
                load_img("Falling/Falling4.png"),
                load_img("Falling/Falling5.png"),
                load_img("Falling/Falling6.png"),
            ],
            "rising": [
                load_img("Rising/Rising1.png"),
                load_img("Rising/Rising2.png"),
                load_img("Rising/Rising3.png"),
                load_img("Rising/Rising4.png"),
                load_img("Rising/Rising5.png"),
                load_img("Rising/Rising6.png"),
            ],
            "attack": [
                load_img("Attack/StaffWood/AttackWood1.png"),
                load_img("Attack/StaffWood/AttackWood2.png"),
                load_img("Attack/StaffWood/AttackWood3.png"),
                load_img("Attack/StaffWood/AttackWood4.png"),
                load_img("Attack/StaffWood/AttackWood5.png"),
                load_img("Attack/StaffWood/AttackWood6.png"),
            ],
        }

        self.large_platform = pygame.Surface(
            (self.screen_width - 150, 100), pygame.SRCALPHA
        )

        for i in range((self.screen_width - 150) // self.platform.get_width() + 1):
            self.large_platform.blit(self.platform, (i * self.platform.get_width(), 0))
        

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("gray")

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.playerAirborne:
                self.playerVelocity -= 3
                self.playerAirborne = True
            if keys[pygame.K_d] and self.playerAirborne:
                self.playerVelocity += 0.1
            if keys[pygame.K_s]:
                self.player_pos.x -= 2
                self.lastDirection = "left"
                if not self.playerAirborne:
                    self.currentAnimation = "run"
            if keys[pygame.K_f]:
                self.lastDirection = "right"
                self.player_pos.x += 2
                if not self.playerAirborne:
                    self.currentAnimation = "run"
            if keys[pygame.K_j] and not keys[pygame.K_s] and not keys[pygame.K_f]:
                self.animationStage = 0
                self.currentAnimation = "attack"

            if self.playerAirborne:
                if self.playerVelocity < 0:
                    self.currentAnimation = "rising"
                else:
                    self.currentAnimation = "falling"
                self.playerVelocity = min(self.player_terminal_velocity, self.playerVelocity + 0.12)
                self.player_pos.y += self.playerVelocity

            player_hitbox = pygame.Rect(
                self.player_pos.x,
                self.player_pos.y,
                self.player.get_width(),
                self.player.get_height(),
            )
            platform_hitbox = pygame.Rect(
                75,
                self.canvas_height - 16,
                self.large_platform.get_width(),
                self.large_platform.get_height(),
            )

            if player_hitbox.colliderect(platform_hitbox):
                self.playerVelocity = 0
                self.playerAirborne = False
                player_hitbox.bottom = platform_hitbox.top
                self.player_pos.y = player_hitbox.bottom - player_hitbox.height


            # stuff to render
            player_surf = self.player_animations[self.currentAnimation][self.animationStage // 5]
            player_coord = (self.player_pos.x, self.player_pos.y)

            # special rendering for attack
            if self.currentAnimation == "attack":
                player_coord = (self.player_pos.x, self.player_pos.y - 48)

            # render the player and render according to if moving right or left
            if self.lastDirection == "left":
                player_surf = pygame.transform.flip(player_surf, True, False)

            # cycle animation
            if self.animationStage >= 25:
                self.animationStage = 0
                if self.currentAnimation == "attack":
                    self.currentAnimation = "idle"
            else:
                self.animationStage += 1

            # finally... render
            self.canvas.fill("gray")
            self.canvas.blit(self.map.render(self.canvas), (0, 0))
            self.canvas.blit(player_surf, player_coord)
            
            self.screen.blit(pygame.transform.scale_by(self.canvas, 4), (0, 0))

            # idle animation
            if (
                self.playerVelocity == 0
                and not self.playerAirborne
                and self.currentAnimation != "attack"
            ):
                self.currentAnimation = "idle"

            # refresh the screen
            pygame.display.update()

            # 60 FPS
            self.clock.tick(60)


Game().run()
