import pygame
from abc import ABC, abstractmethod

from settings import collide, DAMAGE, HP, SHOOTING_VEL, RED_SPACE_SHIP, RED_LASER, GREEN_SPACE_SHIP, GREEN_LASER, \
    BLUE_SPACE_SHIP, BLUE_LASER, YELLOW_SPACE_SHIP, YELLOW_LASER, BOSS, BOSS_LASER, HEIGHT, WIDTH


class Laser:
    TYPES = {"green": 6, "blue": 4, "red": 8, "yellow": -5, "boss": 8}

    def __init__(self, x, y, img, color):
        self.vel = Laser.TYPES[color]
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def off_screen(self, height):
        return not(height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class BossLaser(Laser):
    def __init__(self, x, y, img, color, x_vel):
        super().__init__(x, y, img, color)
        self.x_vel = x_vel

    def move(self):
        self.y += self.vel
        self.x += self.x_vel


class Supply(ABC):
    TYPES = {"damage": DAMAGE, "hp": HP, "shoot": SHOOTING_VEL}

    def __init__(self, x, y, type_):
        self.vel = 2.5
        self.x = x
        self.y = y
        self.type_ = type_
        self.img = pygame.transform.scale(Supply.TYPES[self.type_], (60, 60))
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def off_screen(self, height):
        return self.y + self.get_height() > height

    def collision(self, obj):
        return collide(self, obj)

    def action(self, obj: "Player"):
        if self.type_ == "damage":
            obj.damage += 5
        elif self.type_ == 'hp':
            if obj.health + 30 > obj.max_health:
                obj.health = obj.max_health
            else:
                obj.health += 30
        elif self.type_ == "shoot":
            if obj.cool_down_rate - 2 > 0:
                obj.cool_down_rate -= 2

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()


class Ship(ABC):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER, 1, 30, 9, 60),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER, 1.25, 50, 6, 40),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER, 1.5, 70, 3, 20),
                "yellow": (YELLOW_SPACE_SHIP, YELLOW_LASER, 5, 30, 20, 200),
                "boss": (BOSS, BOSS_LASER, 2, 5, 5, 500)
                }

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.health = self.COLOR_MAP[color][-1]
        self.max_health = self.health
        self.lasers = []
        self.cool_down_counter = 0
        self.color = color
        self.ship_img, self.laser_img, self.vel, self.cool_down_rate, self.damage, _ = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    @abstractmethod
    def healthbar(self, window):
        pass

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
        self.healthbar(window)

    def move_lasers(self, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move()
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= self.damage
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.cool_down_rate:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img, self.color)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):

    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.points = 0

    def move_lasers(self, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move()
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= self.damage
                        if obj.health <= 0:
                            self.points += obj.max_health
                            objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):

    def __init__(self, x, y, color):
        super().__init__(x, y, color)

    def move(self):
        self.y += self.vel

    def shoot(self):
        if self.cool_down_counter == 0:
            if self.color == "blue":
                laser = Laser(self.x - (self.get_width() // 2), self.y, self.laser_img, self.color)
            else:
                laser = Laser(self.x-15, self.y, self.laser_img, self.color)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y - 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y - 10,
                                               self.ship_img.get_width() * (self.health / self.max_health), 10))


class Boss(Enemy):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.x_vel = self.vel

    def shoot(self):
        if self.cool_down_counter == 0:
            for i, j in zip(range(0, 120, 20), range(-8, 12, 4)):
                laser = BossLaser(self.x + i, self.y + self.get_height() - 20, self.laser_img, self.color, j)
                self.lasers.append(laser)
            self.cool_down_counter = 1

    def move(self):
        if self.y + self.get_height() + self.vel < HEIGHT // 3:
            self.y += self.vel
        else:
            if self.x + self.get_width() + self.x_vel < WIDTH and self.x + self.x_vel > 0:
                self.x += self.x_vel
            else:
                self.x_vel = -self.x_vel
