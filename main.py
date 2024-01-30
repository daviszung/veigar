import pygame
import sys

from scripts.utils import load_img, load_audio

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("veigar")

        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        # player
        self.player_pos = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        self.player = pygame.transform.scale_by(
            pygame.image.load("assets/mage/Idle/Idle1.png"), (3, 3)
        ).convert()
        self.player.set_colorkey((0, 0, 0))
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

        self.sfx = {
            "jump": load_audio("jump1.wav", 0.5) 
        }

        sheet = pygame.image.load("assets/sheet.png")
        scaled_sheet = pygame.transform.scale_by(sheet, (4, 4))

        platformTexture = pygame.Rect(512, 320, 64, 145)
        platform = scaled_sheet.subsurface(platformTexture).convert()

        self.large_platform = pygame.Surface(
            (self.screen_width - 150, 100), pygame.SRCALPHA
        )

        for i in range((self.screen_width - 150) // platform.get_width() + 1):
            self.large_platform.blit(platform, (i * platform.get_width(), 0))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("gray")

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.playerAirborne:
                self.playerVelocity -= 4
                self.playerAirborne = True
                self.sfx["jump"].play()
            if keys[pygame.K_d] and self.playerAirborne:
                self.playerVelocity += 0.1
            if keys[pygame.K_s]:
                self.player_pos.x -= 4
                self.lastDirection = "left"
                if not self.playerAirborne:
                    self.currentAnimation = "run"
            if keys[pygame.K_f]:
                self.lastDirection = "right"
                self.player_pos.x += 4
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
                self.playerVelocity += 0.12
                self.player_pos.y += self.playerVelocity

            player_hitbox = pygame.Rect(
                self.player_pos.x,
                self.player_pos.y,
                self.player.get_width(),
                self.player.get_height(),
            )
            platform_hitbox = pygame.Rect(
                75,
                self.screen_height - 80,
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

            # finally... render
            self.screen.blit(player_surf, player_coord)

            # cycle animation
            if self.animationStage >= 25:
                self.animationStage = 0
                if self.currentAnimation == "attack":
                    self.currentAnimation = "idle"
            else:
                self.animationStage += 1

            self.screen.blit(self.large_platform, (75, self.screen_height - 80))

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
