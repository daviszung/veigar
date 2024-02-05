import pygame, os

from typing import List

BASE_ASSET_PATH = "assets/"

BASE_AUDIO_ASSET_PATH = "assets/audio/"


def load_img(path: str):
    img = pygame.image.load(BASE_ASSET_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path: str):
    images: List[pygame.Surface]  = []
    for img_name in sorted(os.listdir(BASE_ASSET_PATH + path)):
        images.append(load_img(path + "/" + img_name))
    return images


# def load_audio(path: str):
#     audio = pygame.mixer.Sound(BASE_AUDIO_ASSET_PATH + path)
#     audio.set_volume(0.5)
#     return audio
