import pygame
import sys

from typing import Dict, List, Tuple

from scripts.utils import load_img
from scripts.tiles import Tilemap
from scripts.projectile import Projectile
from scripts.enemy import Enemy
from scripts.heart_hud import HeartHud
from scripts.malice_hud import MaliceHud
from scripts.player import Player


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

spell_color = pygame.Color(115, 62, 239)
projectile_surface = pygame.Surface((20, 20))


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

        heart_hud_images = {
            "heart": load_img("frames/ui_heart_full.png"),
            "empty_heart": load_img("frames/ui_heart_empty.png"),
        }

        malice_hud_images = {"malice": load_img("purple_sphere.png")}

        # initialize huds and do a single render
        self.heart_hud = HeartHud(heart_hud_images)
        self.heart_hud.update(0)
        self.malice_hud = MaliceHud(malice_hud_images)
        self.malice_hud.update(0)

        self.enemies: List[Enemy] = [
            Enemy(
                "imp",
                20,
                pygame.Rect(150, 144, 16, 16),
            ),
        ]

        self.player = Player()

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
                self.player.y_velocity = 0
                collision_types["bottom"] = True
            elif movement[1] < 0:
                hitbox.top = tile.bottom
                self.player.y_velocity = 0
                collision_types["top"] = True

        return hitbox, collision_types

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            player_x_movement = 0

            if self.player.controls_lock:
                pass
            else:
                keys = pygame.key.get_pressed()
                if (
                    keys[pygame.K_SPACE]
                    and self.player.airtime < 6
                    and self.player.y_velocity >= 0
                ):
                    self.player.y_velocity = -3.5
                if keys[pygame.K_d] and self.player.airtime > 0:
                    self.player.y_velocity += 0.1
                if keys[pygame.K_s]:
                    self.player.flip = True
                    # ensure player doesn't run off screen
                    if self.player.hitbox.x > 0:
                        player_x_movement -= 2
                        self.player.action = "run"
                if keys[pygame.K_f]:
                    self.player.flip = False
                    # ensure player doesn't run off screen
                    if self.player.hitbox.x < (self.canvas_width - self.player.size):
                        player_x_movement += 2
                        self.player.action = "run"
                if keys[pygame.K_j] and not keys[pygame.K_s] and not keys[pygame.K_f]:
                    self.player.action = "attack"
                    self.player.images["attack"] = self.player.images["attack"].copy()

            # find where the player is and what tiles are closest to the player
            player_tile = (
                int(self.player.hitbox.x // 16),
                int(self.player.hitbox.y // 16),
            )
            nearby_tiles: List[Tuple[int, int]] = []
            for i in OFFSET:
                nearby_tiles.append((player_tile[0] + i[0], player_tile[1] + i[1]))

            # create hitboxes for the tiles that are terrain and are close to the player
            nearby_rects: List[pygame.Rect] = []
            for i in nearby_tiles:
                if i in map["grass"]:
                    nearby_rects.append(pygame.Rect(i[0] * 16, i[1] * 16, 16, 16))

            player_coord, collisions = self.move_player(
                self.player.hitbox,
                (player_x_movement, self.player.y_velocity),
                nearby_rects,
            )

            if collisions["bottom"] == True:
                self.player.airtime = 0
            else:
                self.player.airtime += 1

            if self.player.airtime > 6:
                if self.player.y_velocity < 0:
                    self.player.action = "rising"
                if self.player.y_velocity > 0:
                    self.player.action = "falling"

            # check for idling
            if player_x_movement == 0 and self.player.action not in {
                "attack",
                "hit",
                "dying",
            }:
                self.player.action = "idle"

            # stuff to render
            self.player.update()
            player_surf = self.player.images[self.player.action].img()

            # special rendering for attack
            if self.player.action == "attack":
                player_coord = (self.player.hitbox.x, self.player.hitbox.y - 16)

            # render the player and render according to if moving right or left
            if self.player.flip:
                player_surf = pygame.transform.flip(player_surf, True, False)

            # create projectile when casting attack spell
            if (
                self.player.action == "attack"
                and self.player.images[self.player.action].frame == 25
            ):
                if self.player.flip == False:
                    self.projectiles.append(
                        Projectile(
                            projectile_surface,
                            [self.player.hitbox.right, self.player.hitbox.y + 8],
                            [2.5, 0],
                            3,
                            spell_color,
                        )
                    )
                elif self.player.flip:
                    self.projectiles.append(
                        Projectile(
                            projectile_surface,
                            [self.player.hitbox.left, self.player.hitbox.y + 8],
                            [-2.5, 0],
                            3,
                            spell_color,
                        )
                    )

            # enemy collision detection
            for enemy in self.enemies:
                if (
                    enemy.rect.colliderect(self.player.hitbox)
                    and self.player.invincibility_frames == 0
                ):
                    self.player.invincibility_frames = 60
                    self.heart_hud.update(-1)
                    self.player.action = "hit"
                    if self.heart_hud.hearts <= 0:
                        self.player.action = "dying"
                        self.player.controls_lock = True
                    else:
                        # knockback effect
                        self.player.y_velocity -= 2

            # finally... render
            self.canvas.fill("gray")
            self.canvas.blit(self.map.render(self.canvas), (0, 0))
            self.canvas.blit(self.malice_hud.surf, (270, 2))
            self.canvas.blit(self.heart_hud.surf, (4, 4))
            self.canvas.blit(player_surf, player_coord)
            for enemy in self.enemies:
                enemy.update()
                self.canvas.blit(
                    enemy.animations[enemy.type][enemy.action].img(),
                    enemy.rect
                )
            # render projectiles
            for i, p in enumerate(self.projectiles):
                if p.loc[0] < 0 or p.loc[0] > self.canvas_width:
                    p.despawn_mark = True

                p.loc[0] += p.velocity[0]
                p.loc[1] += p.velocity[1]
                pygame.draw.circle(self.canvas, p.color, p.loc, p.radius)

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
