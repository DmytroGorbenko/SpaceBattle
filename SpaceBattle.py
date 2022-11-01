import json
import sys
import pygame

from button import Button
from game import Game, WIN, BG

RULES = "            MOVEMENT:\n\n  W - up\n  A - left\n  S - back\n  D - right\n\n" \
        "            SHOOTING:\n\n  Arrow Key Up - Shot\n\n" \
        "              OTHER:\n\n  SPACE - Pause\n\n\n" \
        "            GAMEPLAY:\n\n" \
        "  ~ Gone - amount of enemies that has gone through your defence! When its up to 10 - you lose!\n" \
        "  ~ Reach level 7 and defeat the BOSS to win!\n" \
        "  ~ Do not let your health bar become fully red!!!\n\n\n" \
        "            SUPPLIES:\n\n  'Thunder' - +2 to your shooting speed\n  '+5' - +5 to your damage\n" \
        "  '+' - +30 to your health" \

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


def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height


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


def rules():
    while True:
        RULES_MOUSE_POS = pygame.mouse.get_pos()
        WIN.blit(BG, (0, 0))

        blit_text(WIN, RULES, (50, 10), get_font(20), pygame.Color("white"))

        RULES_BACK = Button(image=None, pos=(375, 700),
                            text_input="BACK", font=get_font(35), base_color="White", hovering_color="Green")
        RULES_BACK.change_color(RULES_MOUSE_POS)
        RULES_BACK.update(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if RULES_BACK.check_for_input(RULES_MOUSE_POS):
                    main_menu()

        pygame.display.update()


def main_menu():
    while True:
        WIN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(70).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 250),
                             text_input="PLAY", font=get_font(65), base_color="White", hovering_color="Green")
        RESULTS_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 370),
                                text_input="TOP", font=get_font(65), base_color="White", hovering_color="Green")
        RULES_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 490),
                              text_input="RULES", font=get_font(65), base_color="White", hovering_color="Green")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Rect.png"), pos=(350, 610),
                             text_input="QUIT", font=get_font(65), base_color="White", hovering_color="Green")

        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, RESULTS_BUTTON, QUIT_BUTTON, RULES_BUTTON]:
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
                if RULES_BUTTON.check_for_input(MENU_MOUSE_POS):
                    rules()

        pygame.display.update()


if __name__ == "__main__":
    main_menu()
