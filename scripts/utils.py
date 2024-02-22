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


def load_audio(path: str, vol: float):
    audio = pygame.mixer.Sound(BASE_AUDIO_ASSET_PATH + path)
    audio.set_volume(vol)
    return audio

def extract_image(path: str, rects: List[pygame.Rect]):
    base = load_img(path)
    print(base.get_size(), path)
    all_frames: List[pygame.Surface] = []
    for r in rects:
        all_frames.append(base.subsurface(r))
    return all_frames