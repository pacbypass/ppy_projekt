import pygame

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

COLORS = {
    'BACKGROUND': WHITE,
    'TEXT': BLACK,
    'PRIMARY': BLUE,
    'SECONDARY': LIGHT_GRAY,
    'GRAY': GRAY
}

pygame.init()
DEFAULT_FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 48)
LARGE_FONT = pygame.font.Font(None, 32)

FONTS = {
    'DEFAULT': DEFAULT_FONT,
    'TITLE': TITLE_FONT,
    'LARGE': LARGE_FONT
}

MAX_MISTAKES = 6
GAME_MODES = {
    'CLASSIC': 'Klasyczny',
    'TIMED': 'Na czas'
}
TIMED_MODE_DURATION = 120

DATABASE_PATH = 'hangman_game.db'