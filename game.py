import json
import sys

import pygame
import os
import random

from classes import PlayerShip, EnemyShip, BossShip, Supply
from settings import WIN, BG, get_font, WIDTH, HEIGHT, collide


class Game:
    def __init__(self):
        self.run = True
        self.FPS = 60
        self.level = 0
        self.skipped = 0
        self.main_font = pygame.font.SysFont("comicsans", 30)
        self.finish_font = pygame.font.SysFont("comicsans", 30)

        self.enemies = []
        self.wave_length = 0
        self.enemies_types = ['blue', 'green', 'red', 'boss']

        self.supplies = []
        self.supplies_amount = 2
        self.supply_types = ['damage', 'hp', 'shoot']

        self.player = PlayerShip(300, 630, "yellow")
        self.clock = pygame.time.Clock()

        self.lost = False
        self.finish_count = 0
        self.won = False

    def play(self):
        def redraw_window():
            WIN.blit(BG, (0, 0))

            lives_label = get_font(25).render(f"Gone:{self.skipped}", True, (255, 255, 255))
            level_label = get_font(25).render(f"Level:{self.level}", True, (255, 255, 255))
            points_label = get_font(25).render(f"Points:{self.player.points}", True, (255, 255, 255))

            WIN.blit(lives_label, level_label.get_rect(center=(WIN.get_width()*0.15, 30)))
            WIN.blit(level_label, level_label.get_rect(center=(WIN.get_width()*0.85, 30)))
            WIN.blit(points_label, level_label.get_rect(center=(WIN.get_width()*0.43, 30)))

            for enemy in self.enemies:
                enemy.draw(WIN)

            self.player.draw(WIN)

            for sup in self.supplies:
                sup.draw(WIN)

            if self.lost:
                finish_label = get_font(30).render("You Lost!!!", True, (255, 255, 255))
                WIN.blit(finish_label, finish_label.get_rect(center=(375, 330)))
                WIN.blit(points_label, points_label.get_rect(center=(375, 370)))
            elif self.won:
                finish_label = get_font(30).render(f"You Won!!!", True, (255, 255, 255))
                WIN.blit(finish_label, finish_label.get_rect(center=(375, 330)))
                WIN.blit(points_label, points_label.get_rect(center=(375, 370)))

            pygame.display.update()

        def save():
            try:
                with open("results.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if data.get(os.environ.get("USERNAME")) is None:
                        data.update({os.environ.get("USERNAME"): [self.player.points]})
                    else:
                        data[os.environ.get("USERNAME")].append(self.player.points)
            except Exception:
                data = {os.environ.get("USERNAME"): [self.player.points]}
            with open("results.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        def pause():
            paused = True
            pause_label = get_font(30).render("Paused!", True, (255, 255, 255))
            pause_instruction_label = get_font(20).render("Press Q to quit, press C to continue!", True,
                                                          (255, 255, 255))

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
                self.clock.tick(60)

        while self.run:
            self.clock.tick(self.FPS)
            redraw_window()

            if self.skipped >= 10 or self.player.health <= 0:
                self.lost = True
                self.finish_count += 1

            if self.level == "W":
                self.won = True
                self.finish_count += 1

            if self.lost or self.won:
                if self.finish_count > self.FPS * 3:
                    self.run = False
                else:
                    continue

            if len(self.enemies) == 0 and len(self.supplies) == 0:
                if self.level == 7:
                    self.level = "W"
                else:
                    self.level += 1
                self.player.cool_down_rate -= 1
                if self.player.health + self.player.health // 2 > self.player.max_health:
                    self.player.health = self.player.max_health
                else:
                    self.player.health += self.player.health // 2

                if self.level == 7:
                    wave_length = 1
                else:
                    if self.level == 6:
                        wave_length = 17
                    else:
                        wave_length = random.randint(10, 12)

                if self.level != "W" and self.level % 3 == 0:
                    self.supplies_amount += 1

                if self.level == 1:
                    current_enemies = self.enemies_types[0:1]
                elif self.level == 2:
                    current_enemies = self.enemies_types[0:2]
                elif self.level == 3:
                    current_enemies = self.enemies_types[1:2]
                elif self.level == 4:
                    current_enemies = self.enemies_types[1:3]
                elif self.level == 5:
                    current_enemies = self.enemies_types[2:3]
                elif self.level == 6:
                    current_enemies = self.enemies_types[0:3]
                elif self.level == 7:
                    current_enemies = self.enemies_types[-1:]

                if self.level != 7:
                    for _ in range(wave_length):
                        enemy = EnemyShip(random.randrange(100, WIDTH-100), random.randrange(-1100, -100),
                                      random.choice(current_enemies))
                        self.enemies.append(enemy)
                else:
                    if self.won:
                        self.enemies = []
                    else:
                        enemy = BossShip(random.randrange(200, WIDTH-200), random.randrange(-500, -400),
                                     random.choice(current_enemies))
                        self.enemies.append(enemy)

                for _ in range(self.supplies_amount):
                    sup = Supply(random.randrange(100, WIDTH-100), random.randrange(-1800, -1000),
                                 random.choice(self.supply_types))
                    self.supplies.append(sup)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save()
                    pygame.quit()
                    sys.exit(0)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and self.player.x - self.player.vel > 0:
                self.player.x -= self.player.vel
            if keys[pygame.K_d] and self.player.x + self.player.vel + self.player.get_width() < WIDTH:
                self.player.x += self.player.vel
            if keys[pygame.K_w] and self.player.y - self.player.vel > HEIGHT // 2:
                self.player.y -= self.player.vel
            if keys[pygame.K_s] and self.player.y + self.player.vel + self.player.get_height() + 15 < HEIGHT:
                self.player.y += self.player.vel
            if keys[pygame.K_UP]:
                self.player.shoot()
            if keys[pygame.K_SPACE]:
                if pause():
                    self.player.health = 0
                    self.skipped = 10

            for enemy in self.enemies[:]:
                enemy.move()
                enemy.move_lasers(self.player)
                if random.randrange(0, 30) == 1:
                    enemy.shoot()
                if collide(enemy, self.player):
                    self.player.health -= enemy.health // 3
                    self.enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    self.skipped += 1
                    self.enemies.remove(enemy)

            self.player.move_lasers(self.enemies)

            for sup in self.supplies:
                sup.move()
                if sup.off_screen(HEIGHT):
                    self.supplies.remove(sup)
                if sup.collision(self.player):
                    sup.action(self.player)
                    self.supplies.remove(sup)
        save()
