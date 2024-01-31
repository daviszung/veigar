import pygame

BASE_ASSET_PATH = "assets/mage/"

BASE_AUDIO_ASSET_PATH = "assets/audio/"

def load_img(path: str):
    img = pygame.image.load(BASE_ASSET_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

# def load_audio(path: str):
#     audio = pygame.mixer.Sound(BASE_AUDIO_ASSET_PATH + path)
#     audio.set_volume(0.5)
#     return audio