import pygame
import sys
import random
import json
import os


from typing import Dict, List, Tuple

from scripts.utils import load_img, load_audio, center_rect, draw_text
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
from scripts.fire_worm import FireWorm
from scripts.fireball import FireBall
from scripts.button import Button
from scripts.label import Label
from scripts.KeyBindSetting import KeyBindSetting

os.environ["SDL_VIDEO_CENTERED"] = "1"

def saveData(data: object):
    with open("save_file.json", "w+") as file:
        json.dump(data, file)


def readSave():
    data = {
        "sfx_vol": 0.5,
        "music_vol": 0.5,
        "jump": pygame.K_SPACE,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "spell1": pygame.K_j,
    }
    try:
        with open("save_file.json", "r") as file:
            data = json.load(file)

    except FileNotFoundError:
        with open("save_file.json", "w+") as file:
            json.dump(data, file)

    return data


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
        self.game_state = True
        self.menu = "game"
        pygame.init()
        pygame.display.set_caption("veigar")
        pygame.display.set_icon(pygame.image.load("assets/mage/Faces/face_normal.png"))

        self.settings = readSave()
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
        self.enemy_projectiles: List[FireBall] = []

        pygame.mixer.init()
        self.audio_timer = 0

        pygame.mixer.music.load("./assets/audio/main_theme.wav")

        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(self.settings["music_vol"])

        self.audio_groups = {
            "swing": AudioGroup(
                [
                    load_audio("swing1.wav", self.settings["sfx_vol"] * 0.3),
                    load_audio("swing2.wav", self.settings["sfx_vol"] * 0.3),
                    load_audio("swing3.wav", self.settings["sfx_vol"] * 0.3),
                ]
            ),
            "scream": AudioGroup(
                [
                    load_audio("scream1.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("scream2.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("scream3.wav", self.settings["sfx_vol"] * 0.4),
                ]
            ),
            "hit": AudioGroup(
                [
                    load_audio("hitB1.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hitB2.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hitB3.wav", self.settings["sfx_vol"] * 0.4),
                ]
            ),
            "mawface_hit": AudioGroup(
                [load_audio("mawface_hit.wav", self.settings["sfx_vol"] * 0.5)]
            ),
            "mawface_spawn": AudioGroup(
                [load_audio("mawface_spawn.wav", self.settings["sfx_vol"] * 0.5)]
            ),
            "mawface_death": AudioGroup(
                [load_audio("mawface_death.wav", self.settings["sfx_vol"] * 0.4)]
            ),
            "hp_up": AudioGroup(
                [
                    load_audio("hp_up1.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hp_up2.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hp_up3.wav", self.settings["sfx_vol"] * 0.4),
                ]
            ),
            "acquire_crystal_staff": AudioGroup(
                [load_audio("acquire_crystal_staff.wav", self.settings["sfx_vol"] * 1)]
            ),
            "spawn_fireball": AudioGroup(
                [
                    load_audio("spawn_fireball1.wav", self.settings["sfx_vol"] * 1.5),
                    load_audio("spawn_fireball2.wav", self.settings["sfx_vol"] * 1.5),
                    load_audio("spawn_fireball3.wav", self.settings["sfx_vol"] * 1.5),
                ]
            ),
            "fw_death": AudioGroup(
                [
                    load_audio("fw_death1.wav", self.settings["sfx_vol"] * 0.5),
                    load_audio("fw_death2.wav", self.settings["sfx_vol"] * 0.6),
                ]
            ),
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
        # self.spawner.pause = True

        self.enemies: List[Enemy] = []

        self.fw = None

        self.item_images = {
            "hp_potion": load_img("frames/flask_big_red.png"),
            "staff_crystal": load_img("mage/Staffs/staff_crystal.png"),
            "staff_mighty": load_img("mage/Staffs/staff_mighty.png"),
        }

        self.items: List[Item] = []

        self.pause_buttons: List[Button] = [
            Button(
                "resume",
                self.resume,
                center_rect(pygame.Rect(0, 40, 110, 20), self.canvas.get_rect(), "x"),
                "Resume",
            ),
            Button(
                "options",
                self.open_options_menu,
                center_rect(pygame.Rect(0, 80, 110, 20), self.canvas.get_rect(), "x"),
                "Options",
            ),
            Button(
                "quit",
                self.quit,
                center_rect(pygame.Rect(0, 120, 110, 20), self.canvas.get_rect(), "x"),
                "Quit",
            ),
        ]

        self.options_buttons: List[Button] = [
            Button(
                "back",
                self.go_to_pause_menu,
                center_rect(pygame.Rect(0, 144, 110, 20), self.canvas.get_rect(), "x"),
                "Back",
            ),
            Button(
                "music_vol_inc",
                self.increment_music_vol,
                pygame.Rect(self.canvas_width - 36, 36, 8, 8),
                ">",
            ),
            Button(
                "music_vol_dec",
                self.decrement_music_vol,
                pygame.Rect(self.canvas_width - 72, 36, 8, 8),
                "<",
            ),
            Button(
                "sfx_vol_inc",
                self.increment_sfx_vol,
                pygame.Rect(self.canvas_width - 36, 72, 8, 8),
                ">",
            ),
            Button(
                "sfx_vol_dec",
                self.decrement_sfx_vol,
                pygame.Rect(self.canvas_width - 72, 72, 8, 8),
                "<",
            ),
        ]

        self.options_labels: List[Label] = [
            Label("music", pygame.Rect(self.canvas_width - 120, 32, 40, 16), "Music"),
            Label("sfx", pygame.Rect(self.canvas_width - 120, 68, 40, 16), "SFX"),
            Label("left", pygame.Rect(10, 10, 40, 14), "left"),
            Label("right", pygame.Rect(10, 30, 40, 14), "right"),
            Label("down", pygame.Rect(10, 50, 40, 14), "down"),
            Label("jump", pygame.Rect(10, 70, 40, 14), "jump"),
            Label("spell1", pygame.Rect(90, 10, 40, 14), "spell1"),
        ]

        self.key_bind_ui: List[KeyBindSetting] = [
            KeyBindSetting(
                1, pygame.Rect(52, 10, 36, 14), int(self.settings["left"]), "left"
            ),
            KeyBindSetting(
                2, pygame.Rect(52, 30, 36, 14), int(self.settings["right"]), "right"
            ),
            KeyBindSetting(
                3, pygame.Rect(52, 50, 36, 14), int(self.settings["down"]), "down"
            ),
            KeyBindSetting(
                4, pygame.Rect(52, 70, 36, 14), int(self.settings["jump"]), "jump"
            ),
            KeyBindSetting(
                5, pygame.Rect(132, 10, 36, 14), int(self.settings["spell1"]), "spell1"
            ),
        ]

        self.selected_key_bind = None

    def resume(self):
        pygame.mixer.music.unpause()
        self.game_state = True

    def quit(self):
        saveData(self.settings)
        pygame.quit()
        sys.exit()

    def increment_sfx_vol(self):
        self.settings["sfx_vol"] = min(1, round(self.settings["sfx_vol"] + 0.1, 2))
        self.refresh_audio_groups()

    def decrement_sfx_vol(self):
        self.settings["sfx_vol"] = max(0, round(self.settings["sfx_vol"] - 0.1, 2))
        self.refresh_audio_groups()

    def increment_music_vol(self):
        self.settings["music_vol"] = min(1, round(self.settings["music_vol"] + 0.1, 2))
        pygame.mixer.music.set_volume(self.settings["music_vol"])

    def decrement_music_vol(self):
        self.settings["music_vol"] = max(0, round(self.settings["music_vol"] - 0.1, 2))
        pygame.mixer.music.set_volume(self.settings["music_vol"])

    def go_to_pause_menu(self):
        self.menu = "pause"

    def open_options_menu(self):
        self.menu = "options"

    def pause(self):
        self.menu = "pause"
        menu_font = pygame.font.Font("./assets/fonts/KodeMonoVariableWeight.ttf", 10)
        light_gray = pygame.Color(220, 220, 220)
        dark_gray = pygame.Color(50, 50, 50)
        purple = pygame.Color(115, 62, 240)
        dark_purple = pygame.Color(75, 42, 240)
        prev_mouse_state = pygame.mouse.get_pressed()

        while not self.game_state:
            # keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    saveData(self.settings)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and self.selected_key_bind:
                    identifier = self.selected_key_bind.id
                    self.selected_key_bind.key = event.key
                    for i, kb in enumerate(self.key_bind_ui):
                        if kb.id == identifier:
                            self.settings[kb.settings_name] = event.key
                            self.key_bind_ui[i] = KeyBindSetting(
                                identifier, kb.rect, event.key, kb.settings_name
                            )
                            self.selected_key_bind = None

            # get the mouse pos and check if colliderect with the text buttons
            mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = (mouse_pos[0] // 4, mouse_pos[1] // 4)
            current_mouse_state = pygame.mouse.get_pressed()
            left_click = False
            if prev_mouse_state[0] and not current_mouse_state[0]:
                left_click = True
            prev_mouse_state = current_mouse_state

            self.canvas.fill(dark_purple)
            if self.menu == "pause":
                for btn in self.pause_buttons:
                    if btn.rect.collidepoint(scaled_mouse_pos):
                        btn.text_color = purple
                        if left_click:
                            btn.callback()
                    else:
                        btn.text_color = dark_gray

                    pygame.draw.rect(self.canvas, light_gray, btn.rect)
                    img = menu_font.render(btn.text, False, btn.text_color)
                    self.canvas.blit(img, center_rect(img.get_rect(), btn.rect))
            elif self.menu == "options":
                for btn in self.options_buttons:
                    if btn.rect.collidepoint(scaled_mouse_pos):
                        btn.text_color = purple
                        if left_click:
                            btn.callback()
                    else:
                        btn.text_color = dark_gray

                    pygame.draw.rect(self.canvas, light_gray, btn.rect)
                    img = menu_font.render(btn.text, False, btn.text_color)
                    self.canvas.blit(img, center_rect(img.get_rect(), btn.rect))

                for label in self.options_labels:
                    img = menu_font.render(label.text, False, dark_gray)
                    pygame.draw.rect(self.canvas, light_gray, label.rect)
                    self.canvas.blit(img, center_rect(img.get_rect(), label.rect))

                img = menu_font.render(
                    str(self.settings["music_vol"]), False, light_gray
                )
                self.canvas.blit(img, (self.canvas_width - 58, 34))
                img = menu_font.render(str(self.settings["sfx_vol"]), False, light_gray)
                self.canvas.blit(img, (self.canvas_width - 58, 70))

                for kb in self.key_bind_ui:
                    self.canvas.blit(kb.surf, kb.rect)
                    if left_click and kb.rect.collidepoint(scaled_mouse_pos):
                        kb.surf = pygame.Surface(kb.rect.size)
                        kb.surf.fill("purple")
                        self.selected_key_bind = kb

            self.screen.blit(pygame.transform.scale_by(self.canvas, 4), (0, 0))

            pygame.display.update()
            self.clock.tick(60)

    def refresh_audio_groups(self):
        self.audio_groups = {
            "swing": AudioGroup(
                [
                    load_audio("swing1.wav", self.settings["sfx_vol"] * 0.3),
                    load_audio("swing2.wav", self.settings["sfx_vol"] * 0.3),
                    load_audio("swing3.wav", self.settings["sfx_vol"] * 0.3),
                ]
            ),
            "scream": AudioGroup(
                [
                    load_audio("scream1.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("scream2.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("scream3.wav", self.settings["sfx_vol"] * 0.4),
                ]
            ),
            "hit": AudioGroup(
                [
                    load_audio("hitB1.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hitB2.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hitB3.wav", self.settings["sfx_vol"] * 0.4),
                ]
            ),
            "mawface_hit": AudioGroup(
                [load_audio("mawface_hit.wav", self.settings["sfx_vol"] * 0.5)]
            ),
            "mawface_spawn": AudioGroup(
                [load_audio("mawface_spawn.wav", self.settings["sfx_vol"] * 0.5)]
            ),
            "mawface_death": AudioGroup(
                [load_audio("mawface_death.wav", self.settings["sfx_vol"] * 0.4)]
            ),
            "hp_up": AudioGroup(
                [
                    load_audio("hp_up1.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hp_up2.wav", self.settings["sfx_vol"] * 0.4),
                    load_audio("hp_up3.wav", self.settings["sfx_vol"] * 0.4),
                ]
            ),
            "acquire_crystal_staff": AudioGroup(
                [load_audio("acquire_crystal_staff.wav", self.settings["sfx_vol"] * 1)]
            ),
            "spawn_fireball": AudioGroup(
                [
                    load_audio("spawn_fireball1.wav", self.settings["sfx_vol"] * 1.5),
                    load_audio("spawn_fireball2.wav", self.settings["sfx_vol"] * 1.5),
                    load_audio("spawn_fireball3.wav", self.settings["sfx_vol"] * 1.5),
                ]
            ),
            "fw_death": AudioGroup(
                [
                    load_audio("fw_death1.wav", self.settings["sfx_vol"] * 0.5),
                    load_audio("fw_death2.wav", self.settings["sfx_vol"] * 0.6),
                ]
            ),
        }

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

    def despawn_entities(
        self,
        entities: (
            List[Enemy]
            | List[Projectile]
            | List[FireBall]
            | List[Particle]
            | List[Item]
        ),
    ):
        for i, e in enumerate(entities):
            if e.despawn_mark:
                del entities[i]

    def hit_player(self, damage: int):
        if self.player.invincibility_frames == 0 and self.heart_hud.hearts > 0:
            self.player.invincibility_frames = 90
            self.heart_hud.update(damage)
            self.audio_groups["hit"].play_random()
            if self.heart_hud.hearts <= 0:
                self.player.action = "dying"
                self.player.controls_lock = True
            else:
                self.player.action = "hit"

    def run(self):
        while self.game_state:
            player_x_movement = 0

            if not pygame.mixer_music.get_busy():
                pygame.mixer.music.load("./assets/audio/main_theme.wav")
                pygame.mixer_music.play(-1)

            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    saveData(self.settings)
                    pygame.quit()
                    sys.exit()

            if keys[pygame.K_p]:
                self.game_state = False
                self.pause()

            if self.player.controls_lock:
                pass
            else:
                if keys[int(self.settings["jump"])]:
                    if self.player.airtime < 6 and self.player.y_velocity >= 0:
                        self.player.y_velocity = -3.7
                    elif (
                        self.player.airtime > 6
                        and self.player.y_velocity > 0
                        and self.player.double_jump
                    ):
                        self.player.y_velocity = -3.5
                        self.player.double_jump = False
                        for i in range(6):
                            self.particles.append(
                                Particle(
                                    [
                                        self.player.hitbox.x + 8,
                                        self.player.hitbox.y + 2,
                                    ],
                                    [i - 3, 0],
                                    random.randint(1, 4),
                                    pygame.Color(225, 205, 205),
                                )
                            )
                if keys[int(self.settings["down"])] and self.player.airtime > 0:
                    self.player.y_velocity += 0.1
                if keys[int(self.settings["left"])]:
                    self.player.flip = True
                    # ensure player doesn't run off screen
                    if self.player.hitbox.x > 0:
                        player_x_movement -= 2
                        self.player.action = "run"
                if keys[int(self.settings["right"])]:
                    self.player.flip = False
                    # ensure player doesn't run off screen
                    if self.player.hitbox.x < (self.canvas_width - self.player.size):
                        player_x_movement += 2
                        self.player.action = "run"
                if (
                    keys[int(self.settings["spell1"])]
                    and not keys[int(self.settings["left"])]
                    and not keys[int(self.settings["right"])]
                ):
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
                self.player.double_jump = True
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
            if self.player.airtime > 6 and self.player.action != "dying":
                if self.player.y_velocity < 0:
                    self.player.action = "rising"
                if self.player.y_velocity > 0:
                    self.player.action = "falling"

            # RENDERING
            self.player.update()

            # special rendering for attack
            if self.player.action in {"attack", "attack_crystal"}:
                player_coord = (self.player.hitbox.x, self.player.hitbox.y - 16)

            # create projectile when casting attack spell
            if (
                self.player.action == "attack" or self.player.action == "attack_crystal"
            ) and self.player.images[self.player.action].frame == 25:
                self.audio_groups["swing"].play_random()

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
            tick_info = self.spawner.tick(self.enemies, self.player.malice)
            if tick_info["spawned"] == "mawface":
                self.audio_groups["mawface_spawn"].play_random()

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
                if enemy.rect.colliderect(self.player.hitbox):
                    self.hit_player(-1)
                    if enemy.type == "mawface":
                        self.audio_groups["mawface_hit"].play_random()

            # collision detect with attacks against enemies
            for projectile in self.projectiles:
                for enemy in self.enemies:
                    if projectile.rect.colliderect(enemy.rect):
                        enemy.hp -= (self.player.malice // 3) + 1
                        # hp bar updates when hit
                        enemy.hp_bar.fill("black")
                        pygame.draw.rect(
                            enemy.hp_bar,
                            "red",
                            (
                                0,
                                0,
                                (enemy.hp_bar.get_width() * enemy.hp / enemy.max_hp),
                                1,
                            ),
                        )

                        # enemy death
                        if enemy.hp <= 0:
                            enemy.despawn_mark = True

                            # play death sound
                            if enemy.type == "mawface":
                                self.audio_groups["mawface_death"].play_random()
                            elif enemy.type == "imp":
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

                            self.player.malice += enemy.malice_reward
                            self.malice_hud.update(self.player.malice)
                            if self.player.malice == 100:
                                pygame.mixer.music.load(
                                    "./assets/audio/fire_worm_battle.wav"
                                )
                                pygame.mixer.music.play(-1)
                                pygame.mixer.music.set_volume(
                                    self.settings["music_vol"]
                                )
                                self.spawner.pause = True
                                self.fw = FireWorm([2, 0])
                                self.enemies.clear()

                            # chance of dropping item
                            if random.randint(1, enemy.drop_chance) == 1:
                                self.items.append(
                                    Item(
                                        self.item_images["hp_potion"],
                                        "hp_potion",
                                        pygame.Rect(
                                            enemy.rect.x + enemy.offset[0],
                                            enemy.rect.y + enemy.offset[1],
                                            16,
                                            16,
                                        ),
                                        900,
                                    )
                                )

                        projectile.despawn_mark = True

            # enemy projectile logic
            for p in self.enemy_projectiles:
                if p.rect.colliderect(self.player.hitbox):
                    self.hit_player(-1)
                if p.rect.x < 0 or p.rect.x > self.canvas_width:
                    p.despawn_mark = True

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
                                    [
                                        self.player.hitbox.x + 8,
                                        self.player.hitbox.y + 8,
                                    ],
                                    [random.randint(-3, 3), random.randint(3, 7) * -1],
                                    random.randint(3, 7),
                                    random.choice(
                                        [
                                            pygame.Color(65, 59, 236),
                                            pygame.Color(104, 174, 253),
                                        ]
                                    ),
                                )
                            )

            # RENDERING
            self.canvas.fill("cornflowerblue")
            self.map.render(self.canvas)

            # render particles
            for particle in self.particles:
                particle.update()
                pygame.draw.circle(
                    self.canvas, particle.color, particle.loc, particle.timer
                )

            # render enemies
            for enemy in self.enemies:
                enemy.update()
                self.canvas.blit(
                    pygame.transform.flip(
                        enemy.animations[enemy.type][enemy.action].img(),
                        enemy.flip,
                        False,
                    ),
                    (enemy.rect.x + enemy.offset[0], enemy.rect.y + enemy.offset[1]),
                )

                # render hp bar
                self.canvas.blit(
                    enemy.hp_bar,
                    (enemy.rect.x + enemy.offset[0], enemy.rect.y + enemy.offset[1]),
                )

            # fireworm
            if self.fw:
                self.fw.update()
                tiles = self.getNearbyRects(self.fw.rect)
                if self.player.hitbox.x < self.fw.rect.x:
                    self.fw.flip = True
                    if self.fw.action == "walk":
                        self.fw.move(-1, tiles)
                    else:
                        self.fw.move(0, tiles)
                elif self.player.hitbox.x > self.fw.rect.x:
                    self.fw.flip = False
                    if self.fw.action == "walk":
                        self.fw.move(1, tiles)
                    else:
                        self.fw.move(0, tiles)

                if (
                    self.fw.rect.colliderect(self.player.hitbox)
                    and self.fw.action != "death"
                ):
                    self.hit_player(-1)

                # fw hp bar
                self.canvas.blit(self.fw.hp_bar, (10, 164))

                for p in self.projectiles:
                    if self.fw.rect.colliderect(p.rect):
                        self.fw.hp -= (self.player.malice // 3) + 1
                        self.fw.hp_bar.fill("black")
                        # hp bar updates when hit
                        pygame.draw.rect(
                            self.fw.hp_bar,
                            "red",
                            (
                                1,
                                1,
                                (
                                    self.fw.hp_bar.get_width()
                                    * self.fw.hp
                                    / self.fw.max_hp
                                )
                                - 1,
                                6,
                            ),
                        )

                        if self.fw.hp <= 0 and self.fw.action != "death":
                            self.fw.action = "death"
                            self.audio_groups["fw_death"].play_random()
                            self.player.malice += 10
                            self.malice_hud.update(self.player.malice)

                            # drop crystal staff
                            self.items.append(
                                Item(
                                    self.item_images["staff_crystal"],
                                    "staff_crystal",
                                    pygame.Rect(
                                        self.fw.rect.center[0] + self.fw.offset[0],
                                        self.fw.rect.center[1] + self.fw.offset[1],
                                        16,
                                        16,
                                    ),
                                    1800,
                                )
                            )
                            # fade out song and start new song
                            pygame.mixer_music.fadeout(8000)

                        p.despawn_mark = True

                # handle attack
                if (
                    self.fw.action == "attack"
                    and self.fw.animations["attack"].frame
                    / self.fw.animations["attack"].img_dur
                    == 12
                ):
                    loc = [0, 0]
                    vel = [0, 0]
                    if self.fw.flip:
                        loc = [self.fw.rect.x, self.fw.rect.y]
                        vel = [-1, 0]
                    else:
                        loc = [self.fw.rect.topright[0], self.fw.rect.y + 4]
                        vel = [1, 0]
                    self.enemy_projectiles.append(
                        FireBall(loc, vel, self.fw.flip),
                    )
                    self.enemy_projectiles.append(
                        FireBall(loc, [vel[0], vel[1] + 1], self.fw.flip)
                    )
                    self.enemy_projectiles.append(
                        FireBall(loc, [vel[0], vel[1] - 1], self.fw.flip),
                    )
                    self.audio_groups["spawn_fireball"].play_random()

                # render fireworm
                self.canvas.blit(
                    pygame.transform.flip(
                        self.fw.animations[self.fw.action].img(), self.fw.flip, False
                    ),
                    (
                        self.fw.rect.x + self.fw.offset[0],
                        self.fw.rect.y + self.fw.offset[1],
                    ),
                )

            # render player
            self.canvas.blit(
                pygame.transform.flip(
                    self.player.images[self.player.action].img(),
                    self.player.flip,
                    False,
                ),
                player_coord,
            )

            # render projectiles
            for p in self.projectiles:
                if p.rect.x < 0 or p.rect.x > self.canvas_width:
                    p.despawn_mark = True

                p.rect.x += p.velocity[0]
                p.rect.y += p.velocity[1]
                pygame.draw.circle(self.canvas, p.color, (p.rect.x, p.rect.y), p.radius)

                self.particles.append(
                    Particle(
                        [p.rect.x, p.rect.y],
                        [random.randint(-2, 2), random.randint(-2, 2)],
                        random.randint(1, 3),
                        p.color,
                    )
                )

            # render enemy projectiles
            for p in self.enemy_projectiles:
                p.rect.x += p.velocity[0]
                p.rect.y += p.velocity[1]
                p.update()
                img = p.animations[p.action].img()
                offset = [0, 0]
                if p.velocity[1] < 0:
                    img = pygame.transform.rotate(img, 45)
                    offset = [-2, -4]

                elif p.velocity[1] > 0:
                    img = pygame.transform.rotate(img, -45)
                    offset = [-2, -4]

                self.canvas.blit(
                    pygame.transform.flip(img, p.flip, False),
                    (p.rect.x + offset[0], p.rect.y + offset[1]),
                )

            # render items
            for item in self.items:
                item.update()
                self.canvas.blit(item.image, item.rect)

            # render HUDs
            self.canvas.blit(self.malice_hud.surf, (270, 2))
            self.canvas.blit(self.heart_hud.surf, (4, 4))

            # when dead
            if self.heart_hud.hearts <= 0:
                font = pygame.font.Font("./assets/fonts/KodeMonoVariableWeight.ttf", 10)
                s = pygame.Surface((100, 20))
                s.fill((115, 62, 240))
                draw_text(
                    s,
                    "Restart?",
                    font,
                    pygame.Color(255, 255, 255),
                    center_rect(pygame.Rect(0, 0, 40, 16), s.get_rect()),
                )
                centered_surf_rect = center_rect(s.get_rect(), self.canvas.get_rect())
                self.canvas.blit(s, centered_surf_rect)
                mouse_pos = pygame.mouse.get_pos()
                scaled_mouse_pos = (mouse_pos[0] // 4, mouse_pos[1] // 4)
                current_mouse_state = pygame.mouse.get_pressed()
                if (
                    centered_surf_rect.collidepoint(scaled_mouse_pos)
                    and current_mouse_state[0] == True
                ):
                    saveData(self.settings)
                    pygame.quit()
                    self.__init__()
                    

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

            # despawn marked entities
            self.despawn_entities(self.enemies)
            self.despawn_entities(self.particles)
            self.despawn_entities(self.items)
            self.despawn_entities(self.enemy_projectiles)
            if self.fw and self.fw.despawn_mark:
                self.spawner.pause = False
                for i in range(30):
                    self.particles.append(
                        Particle(
                            [self.fw.rect.centerx, self.fw.rect.centery],
                            [random.randint(-3, 3), random.randint(-3, 3)],
                            random.randint(2, 8),
                            random.choice(
                                [
                                    pygame.Color(193, 60, 60),
                                    pygame.Color(132, 15, 15),
                                ]
                            ),
                        )
                    )
                self.fw = None

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
