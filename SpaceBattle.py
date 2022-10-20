import json
import os
import sys
import pygame

from button import Button
from game import Game, WIDTH, HEIGHT, WIN, BG

pygame.font.init()
pygame.display.set_caption("SpaceBattle")


def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


def get_top():
    try:
        with open("results.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            top = []
            for i in data.values():
                for j in i:
                    top.append(j)
            top.sort()
            return top[-10:]
    except Exception:
        return []


def top():
    while True:
        TOP_MOUSE_POS = pygame.mouse.get_pos()

        WIN.blit(BG, (0, 0))

        TOP_TEXT = get_font(35).render("TOP-10", True, "White")
        TOP_RECT = TOP_TEXT.get_rect(center=(375, 50))
        WIN.blit(TOP_TEXT, TOP_RECT)

        points = "Points"
        TEXT = get_font(30).render(f"№.       {points}", True, "White")
        RECT = TEXT.get_rect(center=(375, 150))
        WIN.blit(TEXT, RECT)

        top_list = get_top()
        for i, j in enumerate(zip(reversed(top_list), range(230, 680, 40)), 1):
            TEXT = get_font(30).render(f"{i}.     {j[0]:7}", True, "White")
            RECT = TEXT.get_rect(center=(375, j[1]))
            WIN.blit(TEXT, RECT)


        TOP_BACK = Button(image=None, pos=(375, 700),
                            text_input="BACK", font=get_font(35), base_color="White", hovering_color="Green")

        TOP_BACK.change_color(TOP_MOUSE_POS)
        TOP_BACK.update(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if TOP_BACK.check_for_input(TOP_MOUSE_POS):
                    main_menu()

        pygame.display.update()


def main_menu():
    while True:
        WIN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(55).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 250),
                             text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        RESULTS_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 400),
                                text_input="TOP", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 550),
                             text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, RESULTS_BUTTON, QUIT_BUTTON]:
            button.change_color(MENU_MOUSE_POS)
            button.update(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.check_for_input(MENU_MOUSE_POS):
                    game = Game()
                    game.play()
                if RESULTS_BUTTON.check_for_input(MENU_MOUSE_POS):
                    top()
                if QUIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


if __name__ == "__main__":
    main_menu()
