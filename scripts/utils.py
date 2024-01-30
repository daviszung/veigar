import pygame

BASE_ASSET_PATH = "assets/mage/"

BASE_AUDIO_ASSET_PATH = "assets/audio/"

pygame.mixer.init()

def load_img(path: str):
    img = pygame.transform.scale_by(pygame.image.load(BASE_ASSET_PATH + path), (3, 3)).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_audio(path: str):
    audio = pygame.mixer.Sound(BASE_AUDIO_ASSET_PATH + path)
    audio.set_volume(0.5)
    return audio