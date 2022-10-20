import json
import pygame
import os
import random
from abc import ABC, abstractmethod

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


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


class Game:
    def play(self):
        run = True
        FPS = 60
        level = 0
        lives = 0
        main_font = pygame.font.SysFont("comicsans", 30)
        finish_font = pygame.font.SysFont("comicsans", 30)

        enemies = []
        wave_length = 0
        enemies_types = ['blue', 'green', 'red', 'boss']

        supplies = []
        supplies_amount = 2
        supply_types = ['damage', 'hp', 'shoot']

        player = Player(300, 630, "yellow")
        clock = pygame.time.Clock()

        lost = False
        finish_count = 0
        won = False

        def redraw_window():
            WIN.blit(BG, (0, 0))
            # draw text
            lives_label = get_font(25).render(f"Gone:{lives}", 1, (255, 255, 255))
            level_label = get_font(25).render(f"Level:{level}", 1, (255, 255, 255))
            points_label = get_font(25).render(f"Points:{player.points}", 1, (255, 255, 255))

            WIN.blit(lives_label, level_label.get_rect(center=(WIN.get_width()*0.15, 30)))
            WIN.blit(level_label, level_label.get_rect(center=(WIN.get_width()*0.85, 30)))
            WIN.blit(points_label, level_label.get_rect(center=(WIN.get_width()*0.43, 30)))

            for enemy in enemies:
                enemy.draw(WIN)

            player.draw(WIN)

            for sup in supplies:
                sup.draw(WIN)

            if lost:
                finish_label = get_font(30).render("You Lost!!!", 1, (255, 255, 255))
                WIN.blit(finish_label, finish_label.get_rect(center=(375, 330)))
                WIN.blit(points_label, points_label.get_rect(center=(375, 370)))
            elif won:
                finish_label = get_font(30).render(f"You Won!!!", 1, (255, 255, 255))
                WIN.blit(finish_label, finish_label.get_rect(center=(375, 330)))
                WIN.blit(points_label, points_label.get_rect(center=(375, 370)))

            pygame.display.update()

        def save():
            data = {}
            try:
                with open("results.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if data.get(os.environ.get("USERNAME")) is None:
                        data.update({os.environ.get("USERNAME"): [player.points]})
                    else:
                        data[os.environ.get("USERNAME")].append(player.points)
            except Exception:
                    data = {os.environ.get("USERNAME"): [player.points]}
            with open("results.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        def pause():
            paused = True
            pause_label = get_font(30).render("Paused!", 1, (255, 255, 255))
            pause_instruction_label = get_font(20).render("Press Q to quit, press C to continue!", 1, (255, 255, 255))

            while paused:
                WIN.blit(pause_label, pause_label.get_rect(center=(375, 330)))
                WIN.blit(pause_instruction_label, pause_instruction_label.get_rect(center=(375, 370)))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save()
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            paused = False
                        elif event.key == pygame.K_q:
                            return True
                pygame.display.update()
                clock.tick(5)

        while run:
            clock.tick(FPS)
            redraw_window()

            if lives >= 10 or player.health <= 0:
                lost = True
                finish_count += 1

            if level == 8:
                won = True
                finish_count += 1

            if lost or won:
                if finish_count > FPS * 3:
                    run = False
                else:
                    continue

            if len(enemies) == 0 and len(supplies) == 0:
                level += 1
                player.cool_down_rate -= 1
                if player.health + player.health // 2 > player.max_health:
                    player.health = player.max_health
                else:
                    player.health += player.health // 2

                if level == 7:
                    wave_length = 1
                else:
                    if level == 6:
                        wave_length = 15
                    else:
                        wave_length = random.randint(10, 12)

                if level % 3 == 0:
                    supplies_amount += 1

                if level == 1:
                    current_enemies = enemies_types[0:1]
                elif level == 2:
                    current_enemies = enemies_types[0:2]
                elif level == 3:
                    current_enemies = enemies_types[1:2]
                elif level == 4:
                    current_enemies = enemies_types[1:3]
                elif level == 5:
                    current_enemies = enemies_types[2:3]
                elif level == 6:
                    current_enemies = enemies_types[0:3]
                elif level == 7:
                    current_enemies = enemies_types[-1:]

                if level != 7:
                    for _ in range(wave_length):
                        enemy = Enemy(random.randrange(100, WIDTH-100), random.randrange(-1100, -100),
                                      random.choice(current_enemies))
                        enemies.append(enemy)
                else:
                    enemy = Boss(random.randrange(200, WIDTH-200), random.randrange(-500, -400),
                                 random.choice(current_enemies))
                    enemies.append(enemy)

                for _ in range(supplies_amount):
                    sup = Supply(random.randrange(100, WIDTH-100), random.randrange(-1800, -1000),
                                 random.choice(supply_types))
                    supplies.append(sup)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save()
                    pygame.quit()
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.x - player.vel > 0:
                player.x -= player.vel
            if keys[pygame.K_d] and player.x + player.vel + player.get_width() < WIDTH:
                player.x += player.vel
            if keys[pygame.K_w] and player.y - player.vel > HEIGHT // 2:
                player.y -= player.vel
            if keys[pygame.K_s] and player.y + player.vel + player.get_height() + 15 < HEIGHT:
                player.y += player.vel
            if keys[pygame.K_UP]:
                player.shoot()
            if keys[pygame.K_SPACE]:
                if pause():
                    player.health = 0
                    lives = 10

            for enemy in enemies[:]:
                enemy.move()
                enemy.move_lasers(player)
                if random.randrange(0, 30) == 1:
                    enemy.shoot()
                if collide(enemy, player):
                    player.health -= enemy.health // 3
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives += 1
                    enemies.remove(enemy)

            player.move_lasers(enemies)

            for sup in supplies:
                sup.move()
                if sup.off_screen(HEIGHT):
                    supplies.remove(sup)
                if sup.collision(player):
                    sup.action(player)
                    supplies.remove(sup)
        save()
