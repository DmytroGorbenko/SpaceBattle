import pygame
import os


WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Enemies
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
BOSS = pygame.image.load(os.path.join("assets", "boss.png"))

# Player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
BOSS_LASER = pygame.image.load(os.path.join("assets", "boss_laser.png"))


# Supplies
DAMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "damage.png")), (WIDTH, HEIGHT))
HP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "hp.png")), (WIDTH, HEIGHT))
SHOOTING_VEL = pygame.transform.scale(pygame.image.load(os.path.join("assets", "veloc.png")), (WIDTH, HEIGHT))


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None
