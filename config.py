import pygame
from enum import Enum
import os

# Window Settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600  # Make it square like in the image
GRID_SIZE = 20  # Grid cell size
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
WRAP_AROUND = True  # Allow snake to go through borders
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 200, 255)

# Game Settings
INITIAL_SNAKE_LENGTH = 3
INITIAL_SPEED = 10
MAX_SPEED = 20
SPEED_INCREMENT = 0.8
POINTS_PER_FOOD = 20
EVOLUTION_POINTS = 80

# Abilities
TELEPORT_COOLDOWN = 3000
DASH_COOLDOWN = 2000
CLONE_COOLDOWN = 8000

# Sound Settings
MUSIC_VOLUME = 0.3
SOUND_VOLUME = 0.5

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Evolution Levels
class Evolution(Enum):
    BASIC = 0
    TELEPORTER = 1
    DASHER = 2
    CLONER = 3

# Asset Paths
ASSET_DIR = "assets"
FONT_PATH = os.path.join(ASSET_DIR, "fonts")
SOUND_PATH = os.path.join(ASSET_DIR, "sounds")
IMAGE_PATH = os.path.join(ASSET_DIR, "images")

# Font Settings
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18

# Map Types
class MapType(Enum):
    EMPTY = "empty"
    OBSTACLES = "obstacles"
    MAZE = "maze"
    PORTAL = "portal"

# Skins
class SnakeSkin(Enum):
    CLASSIC = "classic"
    NEON = "neon"
    PIXEL = "pixel"
    RAINBOW = "rainbow"

# Button Styles
class ButtonStyle(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DANGER = "danger"
    SUCCESS = "success"

# Create asset directories if they don't exist
for directory in [ASSET_DIR, FONT_PATH, SOUND_PATH, IMAGE_PATH]:
    if not os.path.exists(directory):
        os.makedirs(directory) 