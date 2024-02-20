import pygame
import sys
import random

from typing import Dict, List, Tuple

from scripts.utils import load_img, load_audio
from scripts.tiles import Tilemap
from scripts.projectile import Projectile
from scripts.enemy import Enemy
from scripts.spawner import Spawner
from scripts.heart_hud import HeartHud
from scripts.malice_hud import MaliceHud
from scripts.player import Player
from scripts.particle import Particle
from scripts.audio_group import AudioGroup
from scripts.item import Item


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
    (2, 0),
    (2, -1),
    (2, 1),
    (-2, 0),
    (-2, -1),
    (-2, 1),
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

        self.particles: List[Particle] = []

        self.player = Player()

        self.projectiles: List[Projectile] = []

        pygame.mixer.init()
        self.audio_timer = 0

        pygame.mixer.music.load("./assets/audio/mainTheme1.wav")

        pygame.mixer.music.play(-1)

        self.audio_groups = {
            # "jump": load_audio("jump1.wav", 0.2),
            # "landing": load_audio("landingOnGround.wav", 0.5),
            "scream": AudioGroup(
                [
                    load_audio("scream1.wav", 0.4),
                    load_audio("scream2.wav", 0.4),
                    load_audio("scream3.wav", 0.4),
                ]
            ),
            "hit": AudioGroup(
                [
                    load_audio("hitB1.wav", 0.4),
                    load_audio("hitB2.wav", 0.4),
                    load_audio("hitB3.wav", 0.4),
                ]
            ),
            "hp_up": AudioGroup(
                [
                    load_audio("hp_up1.wav", 0.4),
                    load_audio("hp_up2.wav", 0.4),
                    load_audio("hp_up3.wav", 0.4),
                ]
            ),
            "acquire_crystal_staff": AudioGroup([load_audio("acquire_crystal_staff.wav", 1)])
        }

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

        self.item_images = {
            "hp_potion": load_img("frames/flask_big_red.png"),
            "staff_crystal": load_img("mage/Staffs/staff_crystal.png"),
            "staff_mighty": load_img("mage/Staffs/staff_mighty.png"),
        }

        self.items: List[Item] = []

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
                    if self.player.staff == "wood":
                        self.player.action = "attack"
                        self.player.images["attack"] = self.player.images[
                            "attack"
                        ].copy()
                    elif self.player.staff == "crystal":
                        self.player.action = "attack_crystal"
                        self.player.images["attack_crystal"] = self.player.images[
                            "attack_crystal"
                        ].copy()

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
                "attack_crystal",
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

            # special rendering for attack
            if self.player.action == "attack" or self.player.action == "attack_crystal":
                player_coord = (self.player.hitbox.x, self.player.hitbox.y - 16)

            # create projectile when casting attack spell
            if (
                self.player.action == "attack" or self.player.action == "attack_crystal"
            ) and self.player.images[self.player.action].frame == 25:
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
            self.spawner.tick(self.enemies, self.player.malice)

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
                    if self.heart_hud.hearts <= 0:
                        self.player.action = "dying"
                        self.player.controls_lock = True
                    else:
                        self.player.action = "hit"
                        self.audio_groups["hit"].play_random()

            # collision detect with attacks against enemies
            for projectile in self.projectiles:
                for enemy in self.enemies:
                    if projectile.rect.colliderect(enemy.rect):
                        enemy.hp -= (self.player.malice // 3) + 1
                        if enemy.hp <= 0:
                            # enemy death
                            enemy.despawn_mark = True
                            self.audio_groups["scream"].play_random()
                            for i in range(10):
                                self.particles.append(
                                    Particle(
                                        [enemy.rect.x + 8, enemy.rect.y + 8],
                                        [random.randint(-3, 3), random.randint(-3, 3)],
                                        random.randint(2, 4),
                                        pygame.Color(
                                            random.randint(0, 255),
                                            random.randint(0, 255),
                                            random.randint(0, 255),
                                        ),
                                    )
                                )

                            self.player.malice += 1
                            self.malice_hud.update(self.player.malice)

                            # chance of dropping item
                            if random.randint(1, 9) == 1:
                                self.items.append(
                                    Item(
                                        self.item_images["hp_potion"],
                                        "hp_potion",
                                        pygame.Rect(enemy.rect.x, enemy.rect.y, 16, 16),
                                        900,
                                    )
                                )

                        projectile.despawn_mark = True

            # collision detection with items
            for item in self.items:
                if item.rect.colliderect(self.player.hitbox):
                    item.despawn_mark = True
                    if item.kind == "hp_potion":
                        if self.heart_hud.hearts < self.heart_hud.max_hearts:
                            self.audio_groups["hp_up"].play_random()
                        self.heart_hud.update(1)
                    elif item.kind == "staff_crystal":
                        self.player.staff = "crystal"
                        pygame.mixer_music.pause()
                        self.audio_timer = 150
                        self.audio_groups["acquire_crystal_staff"].play_random()
                        for i in range(35):
                            self.particles.append(
                                Particle(
                                    [self.player.hitbox.x + 8, self.player.hitbox.y + 8],
                                    [random.randint(-3, 3), random.randint(3, 7) * -1],
                                    random.randint(3, 7),
                                    random.choice([pygame.Color(65, 59, 236), pygame.Color(104, 174, 253)]),
                                )
                            )

            # finally... render
            self.canvas.fill("cornflowerblue")
            self.map.render(self.canvas)

            # render particles
            for particle in self.particles:
                particle.update()
                pygame.draw.circle(
                    self.canvas, particle.color, particle.loc, particle.timer
                )

            for enemy in self.enemies:
                enemy.update()
                self.canvas.blit(pygame.transform.flip(enemy.animations[enemy.type][enemy.action].img(), enemy.flip, False), (enemy.rect.x + enemy.offset[0], enemy.rect.y + enemy.offset[1]))
                pygame.draw.rect(self.canvas, "blue", (enemy.rect.x, enemy.rect.y, enemy.rect.width, enemy.rect.height))

                # create an HP bar
                hp_bar_surf = pygame.Surface((16, 1))
                hp_bar_surf.fill("black")
                pygame.draw.rect(
                    hp_bar_surf, "red", (0, 0, (16 * enemy.hp / enemy.max_hp), 1)
                )
                self.canvas.blit(hp_bar_surf, (enemy.rect.x + enemy.offset[0], enemy.rect.y + enemy.offset[1]))

            # render player
            self.canvas.blit(pygame.transform.flip(self.player.images[self.player.action].img(), self.player.flip, False), player_coord)
            # pygame.draw.rect(self.canvas, "red", self.player.hitbox)


            # render projectiles
            for p in self.projectiles:
                if p.rect.x < 0 or p.rect.x > self.canvas_width:
                    p.despawn_mark = True

                p.rect.x += p.velocity[0]
                p.rect.y += p.velocity[1]
                pygame.draw.circle(self.canvas, p.color, (p.rect.x, p.rect.y), p.radius)

            # render items
            for item in self.items:
                item.update()
                self.canvas.blit(item.image, item.rect)

            # render HUDs
            self.canvas.blit(self.malice_hud.surf, (270, 2))
            self.canvas.blit(self.heart_hud.surf, (4, 4))

            # scale canvas to screen
            self.screen.blit(pygame.transform.scale_by(self.canvas, 4), (0, 0))

            # despawn projectiles
            for i, p in enumerate(self.projectiles):
                if p.despawn_mark == True:
                    del self.projectiles[i]
                    for i in range(5):
                        self.particles.append(
                            Particle(
                                [p.rect.x, p.rect.y],
                                [random.randint(-3, 3), random.randint(-3, 3)],
                                3,
                                (p.color),
                            )
                        )

            # despawn enemies
            for i, e in enumerate(self.enemies):
                if e.despawn_mark:
                    del self.enemies[i]

            for i, p in enumerate(self.particles):
                if p.despawn_mark:
                    del self.particles[i]

            for i, item in enumerate(self.items):
                if item.despawn_mark:
                    del self.items[i]
            
            # audio timer
            if self.audio_timer > 0:
                self.audio_timer -= 1
                if self.audio_timer <= 0:
                    pygame.mixer_music.unpause()

            # refresh the screen
            pygame.display.update()

            # 60 FPS
            self.clock.tick(60)


Game().run()
