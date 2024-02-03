import pygame
import sys

from typing import Dict, List, Tuple

from scripts.utils import load_img
from scripts.tiles import Tilemap
from scripts.projectile import Projectile


map: Dict[str, List[Tuple[int, int]]] = {
    "grass": [
        (0, 10),
        (1, 10),
        (2, 10),
        (3, 10),
        (4, 10),
        (5, 10),
        (6, 10),
        (7, 10),
        (8, 10),
        (9, 10),
        (10, 10),
        (11, 10),
        (12, 10),
        (13, 10),
        (14, 10),
        (15, 10),
        (16, 10),
        (17, 10),
        (18, 10),
        (19, 10),
        (14, 6),
        (8, 8),
    ]
}

# for detecting terrain nearest to the player
OFFSET = [
    (-1, 1),
    (0, 1),
    (1, 1),
    (-1, 2),
    (0, 2),
    (1, 2),
    (-1, 0),
    (0, 0),
    (1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
]


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("veigar")

        self.screen_width = 1280
        self.screen_height = 704
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.canvas_width = self.screen_width / 4
        self.canvas_height = self.screen_height / 4
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height))
        self.clock = pygame.time.Clock()

        sheet = pygame.image.load("assets/sheet.png")
        self.platform = sheet.subsurface(128, 80, 16, 16).convert()

        self.map = Tilemap(map, self.platform)

        self.projectiles: List[Projectile] = []

        # player
        self.player = load_img("Idle/Idle1.png")
        self.player.set_colorkey((0, 0, 0))
        self.player_size = 16
        self.player_rect = pygame.Rect(0, 0, self.player_size, self.player_size)
        self.player_terminal_velocity = 5
        self.playerYVelocity = 0
        self.playerXVelocity = 0
        self.player_airtime = 0
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

    def collision_test(self, hitbox: pygame.Rect, tiles: List[pygame.Rect]):
        collisions: List[pygame.Rect] = []
        for tile in tiles:
            if hitbox.colliderect(tile):
                collisions.append(tile)
        return collisions

    def move_player(
        self,
        hitbox: pygame.Rect,
        movement: Tuple[float, float],
        tiles: List[pygame.Rect],
    ):
        collision_types = {"top": False, "bottom": False, "right": False, "left": False}
        hitbox.x += movement[0]
        collisions = self.collision_test(hitbox, tiles)
        for tile in collisions:
            if movement[0] > 0:
                hitbox.right = tile.left
                collision_types["right"] = True
            elif movement[0] < 0:
                hitbox.left = tile.right
                collision_types["left"] = True

        hitbox.y += movement[1]
        collisions = self.collision_test(hitbox, tiles)
        for tile in collisions:
            if movement[1] > 0:
                hitbox.bottom = tile.top
                self.playerYVelocity = 0
                collision_types["bottom"] = True
            elif movement[1] < 0:
                hitbox.top = tile.bottom
                self.playerYVelocity = 0
                collision_types["top"] = True

        return hitbox, collision_types

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            player_x_movement = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.player_airtime < 6 and self.playerYVelocity >= 0:
                self.playerYVelocity = -3.5
            if keys[pygame.K_d] and self.player_airtime > 0:
                self.playerYVelocity += 0.1
            if keys[pygame.K_s]:
                self.lastDirection = "left"
                # ensure player doesn't run off screen
                if self.player_rect.x > 0:
                    player_x_movement -= 2
                    if self.player_airtime == 0:
                        self.currentAnimation = "run"
            if keys[pygame.K_f]:
                self.lastDirection = "right"
                # ensure player doesn't run off screen
                if self.player_rect.x < (self.canvas_width - self.player_size):
                    player_x_movement += 2
                    if self.player_airtime == 0: 
                        self.currentAnimation = "run"
            if keys[pygame.K_j] and not keys[pygame.K_s] and not keys[pygame.K_f]:
                self.animationStage = 0
                self.currentAnimation = "attack"

            self.playerYVelocity = min(
                self.player_terminal_velocity, self.playerYVelocity + 0.2
            )

            # find where the player is and what tiles are closest to the player
            player_tile = (int(self.player_rect.x // 16), int(self.player_rect.y // 16))
            nearby_tiles: List[Tuple[int, int]] = []
            for i in OFFSET:
                nearby_tiles.append((player_tile[0] + i[0], player_tile[1] + i[1]))

            # create hitboxes for the tiles that are terrain and are close to the player
            nearby_rects: List[pygame.Rect] = []
            for i in nearby_tiles:
                if i in map["grass"]:
                    nearby_rects.append(pygame.Rect(i[0] * 16, i[1] * 16, 16, 16))

            player_coord, collisions = self.move_player(
                self.player_rect,
                (player_x_movement, self.playerYVelocity),
                nearby_rects,
            )

            if collisions["bottom"] == True:
                self.player_airtime = 0
            else:
                self.player_airtime += 1

            if self.player_airtime > 6:
                if self.playerYVelocity < 0:
                    self.currentAnimation = "rising"
                if self.playerYVelocity > 0:
                    self.currentAnimation = "falling"

            # stuff to render
            player_surf = self.player_animations[self.currentAnimation][
                self.animationStage // 5
            ]

            # special rendering for attack
            if self.currentAnimation == "attack":
                player_coord = (self.player_rect.x, self.player_rect.y - 16)

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

            # handle casting an attack spell
            spell_color = pygame.Color(115, 62, 239)
            projectile_surface = pygame.Surface((20, 20))

            if self.currentAnimation == "attack" and self.animationStage == 15:
                if self.lastDirection == "right":
                    self.projectiles.append(
                        Projectile(
                            projectile_surface,
                            [self.player_rect.right, self.player_rect.y + 8],
                            [2.5, 0],
                            3,
                            spell_color,
                        )
                    )
                elif self.lastDirection == "left":
                    self.projectiles.append(
                        Projectile(
                            projectile_surface,
                            [self.player_rect.left, self.player_rect.y + 8],
                            [-2.5, 0],
                            3,
                            spell_color,
                        )
                    )

            # idle animation
            if (
                self.playerYVelocity == 0
                and self.currentAnimation != "attack"
            ):
                self.currentAnimation = "idle"

            # finally... render
            self.canvas.fill("gray")
            self.canvas.blit(self.map.render(self.canvas), (0, 0))
            self.canvas.blit(player_surf, player_coord)
            # render projectiles
            for i, p in enumerate(self.projectiles):
                if p.loc[0] < 0 or p.loc[0] > self.canvas_width:
                    p.despawn_mark = True

                p.loc[0] += p.velocity[0]
                p.loc[1] += p.velocity[1]
                pygame.draw.circle(self.canvas, p.color, p.loc, p.radius)
                # self.canvas.blit(self.basic_spell, p.loc)

            # scale canvas to screen
            self.screen.blit(pygame.transform.scale_by(self.canvas, 4), (0, 0))

            # despawn projectiles
            for i, p in enumerate(self.projectiles):
                if p.despawn_mark == True:
                    del self.projectiles[i]

            # refresh the screen
            pygame.display.update()

            # 60 FPS
            self.clock.tick(60)


Game().run()
