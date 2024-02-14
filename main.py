import pygame
import sys

from typing import Dict, List, Tuple

from scripts.utils import load_img
from scripts.tiles import Tilemap
from scripts.projectile import Projectile
from scripts.enemy import Enemy
from scripts.spawner import Spawner
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
        (11, 8),
        (5, 8),
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

        self.player = Player()

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
        self.malice_hud.update(self.player.malice)

        self.spawner = Spawner()

        self.enemies: List[Enemy] = []

    def collision_test(self, hitbox: pygame.Rect, tiles: List[pygame.Rect]):
        collisions: List[pygame.Rect] = []
        for tile in tiles:
            if hitbox.colliderect(tile):
                collisions.append(tile)
        
        return collisions

    def move(
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
    
    def getNearbyRects(self, rect: pygame.Rect):
        nearby_tiles: List[Tuple[int, int]] = []
        nearby_rects: List[pygame.Rect] = []

        original_tile = (int(rect.x // 16), int(rect.y // 16))
        for i in OFFSET:
            nearby_tiles.append((original_tile[0] + i[0], original_tile[1] + i[1]))
        
        for i in nearby_tiles:
            if i in map["grass"]:
                nearby_rects.append(pygame.Rect(i[0] * 16, i[1] * 16, 16, 16))
        
        return nearby_rects

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
                    self.player.y_velocity = -3.7
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

            # move player
            player_coord, collisions = self.move(
                self.player.hitbox,
                (player_x_movement, self.player.y_velocity),
                self.getNearbyRects(self.player.hitbox),
            )

            if collisions["bottom"] == True:
                self.player.airtime = 0
            else:
                self.player.airtime += 1

            # check for idling
            if player_x_movement == 0 and self.player.action not in {
                "attack",
                "hit",
                "dying",
            }:
                self.player.action = "idle"

            # changing animation in air and factoring in coyote time
            if self.player.airtime > 6:
                if self.player.y_velocity < 0:
                    self.player.action = "rising"
                if self.player.y_velocity > 0:
                    self.player.action = "falling"

            # RENDERING
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
                projectile_info = [self.player.hitbox.right, 3]
                if self.player.flip:
                    projectile_info = [self.player.hitbox.left, -3]

                self.projectiles.append(
                    Projectile(
                        [projectile_info[0], self.player.hitbox.y + 8],
                        [projectile_info[1], 0],
                    )
                )

            # spawn new enemies randomly
            # self.spawner.tick(self.enemies, self.player.malice)

            # move the enemies
            for enemy in self.enemies:
                terrain_near_enemy = self.getNearbyRects(enemy.rect)

                if self.player.hitbox.x < enemy.rect.x:
                    enemy.flip = True
                    enemy.action = "run"
                    enemy.move(-1, self.enemies, terrain_near_enemy)
                elif self.player.hitbox.x > enemy.rect.x:
                    enemy.flip = False
                    enemy.action = "run"
                    enemy.move(1, self.enemies, terrain_near_enemy)
                else:
                    enemy.x_movement = 0
                    enemy.action = "idle"
                    enemy.move(0, self.enemies, terrain_near_enemy)

                # collision detections with enemy hitting the player
                if (
                    enemy.rect.colliderect(self.player.hitbox)
                    and self.player.invincibility_frames == 0
                ):
                    self.player.invincibility_frames = 90
                    self.heart_hud.update(-1)
                    self.player.action = "hit"
                    if self.heart_hud.hearts <= 0:
                        self.player.action = "dying"
                        self.player.controls_lock = True

            # collision detect with attacks against enemies
            for projectile in self.projectiles:
                for enemy in self.enemies:
                    if projectile.rect.colliderect(enemy.rect):
                        enemy.hp -= (self.player.malice // 3) + 1
                        if enemy.hp <= 0:
                            enemy.despawn_mark = True
                            self.player.malice += 1
                            self.malice_hud.update(self.player.malice)
                        projectile.despawn_mark = True

            # finally... render
            self.canvas.fill("gray")
            self.map.render(self.canvas)
            for enemy in self.enemies:
                enemy.update()
                enemy_surf = enemy.animations[enemy.type][enemy.action].img()
                if enemy.flip:
                    enemy_surf = pygame.transform.flip(enemy_surf, True, False)
                self.canvas.blit(enemy_surf, enemy.rect)

            self.canvas.blit(player_surf, player_coord)

            # render projectiles
            for i, p in enumerate(self.projectiles):
                if p.rect.x < 0 or p.rect.x > self.canvas_width:
                    p.despawn_mark = True

                p.rect.x += p.velocity[0]
                p.rect.y += p.velocity[1]
                pygame.draw.circle(self.canvas, p.color, (p.rect.x, p.rect.y), p.radius)

            # render HUDs
            self.canvas.blit(self.malice_hud.surf, (270, 2))
            self.canvas.blit(self.heart_hud.surf, (4, 4))

            # scale canvas to screen
            self.screen.blit(pygame.transform.scale_by(self.canvas, 4), (0, 0))

            # despawn projectiles
            for i, p in enumerate(self.projectiles):
                if p.despawn_mark == True:
                    del self.projectiles[i]

            # despawn enemies
            for i, e in enumerate(self.enemies):
                if e.despawn_mark == True:
                    del self.enemies[i]

            # refresh the screen
            pygame.display.update()

            # 60 FPS
            self.clock.tick(60)


Game().run()
