import pygame
import random
from menu import main_menu
from upload_image import load_image
from game_manager import Game
from config import FPS, CARD_SIZE, K, SUITS, RANKS, SCREEN_WIDTH, SCREEN_HEIGHT


BTN_SIZE = SCREEN_WIDTH / 8, SCREEN_HEIGHT / 16


class Button:
    def __init__(self, screen):
        self.screen = screen
        self.color = (0, 100, 20)
        self.font_small = pygame.font.SysFont(None, 65)
        self.x = 1650
        self.y = 25
        self.text = "Menu"
        self.rect = pygame.draw.rect(self.screen, self.color, (self.x, self.y, *BTN_SIZE), border_radius=25)

    def draw(self):
        self.rect = pygame.draw.rect(self.screen, self.color, (self.x, self.y, *BTN_SIZE), border_radius=25)
        text = self.font_small.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)


class RestartButton(Button):
    def __init__(self):
        super().__init__(screen)
        self.x = 1650
        self.y = 110
        self.text = "Restart"


class StatsButton(Button):
    def __init__(self):
        super().__init__(screen)
        self.x = 1650
        self.y = 195
        self.text = "Statistics"


def move_cards_to_target(cards, target_card):
    for card in cards:
        card.move_to_card(target_card)
        target_card = card


def return_cards_to_position(x, y, cards):
    for card in cards:
        card.move_to(x, y)
        y += 40


class Card:
    def __init__(self, suit, rank, status, kind):
        self.suit = suit
        self.rank = rank
        self.color = "red" if self.suit in ['hearts', 'diamonds'] else "black"
        self.is_movable = True
        self.kind = kind
        self.face_image = load_image("cards", self.suit + "_" + self.rank + ".png", -1)
        self.back_image = load_image("cards", "red_back2.png", -1)
        self.scale()
        self.status = status
        self.image = self.face_image if self.status == "open" else self.back_image
        self.rect = pygame.rect.Rect(50, 50, *CARD_SIZE)

    def get_image(self):
        return self.image

    def change_status(self, status):
        if status == "open":
            self.status = "open"
            self.image = self.face_image
            self.is_movable = True
        elif status == "close":
            self.status = "close"
            self.image = self.back_image
            self.is_movable = False

    def scale(self):
        self.face_image = pygame.transform.scale(self.face_image, CARD_SIZE)
        self.back_image = pygame.transform.scale(self.back_image, CARD_SIZE)

    def move_to_deck(self):
        self.rect.x = deck.drop_deck_rect.x
        self.rect.y = deck.drop_deck_rect.y

    def move_to_card(self, target_card):
        self.rect.x = target_card.rect.x
        self.rect.y = target_card.rect.y + 40

    def move_to(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def move(self, x, y):
        self.rect = self.rect.move(x, y)

    def get_color_and_rank(self):
        if self.status == "open":
            return self.color, self.rank
        return "XX"


class Deck:
    def __init__(self):
        self.deck = []
        self.drop_deck = []
        self.create_deck()
        self.spread_cards()
        self.deck_rect = pygame.rect.Rect(50, 50, *CARD_SIZE)
        self.drop_deck_rect = pygame.rect.Rect(250, 50, *CARD_SIZE)

    def collide_point_for_drop_deck(self, x, y):
        return self.drop_deck_rect.collidepoint(x, y) and self.drop_deck

    def create_deck(self):
        self.deck = [Card(suit, rank, "close", "deck") for suit in SUITS for rank in RANKS]
        random.shuffle(self.deck)

    def draw_card(self, start=False):
        if start:
            if self.deck:
                card = self.deck[0]
                self.deck = self.deck[1:]
                return card
        else:
            if self.drop_deck:
                card = self.drop_deck[-1]
                self.drop_deck = self.drop_deck[:-1]
                return card

    def take_card(self):
        if self.deck:
            card = self.deck[0]
            card.move(200, 0)
            card.change_status("open")
            self.drop_deck.append(card)
            self.deck = self.deck[1:]
        else:
            self.deck = self.drop_deck
            self.drop_deck = []
            [item.move(-200, 0) for item in self.deck]
            [item.change_status("close") for item in self.deck]

    def spread_cards(self):
        y = 300
        for i in range(8):
            flag = True
            for j in range(i, 7):
                card = self.draw_card(True)
                card.kind = "field"
                card.is_movable = flag
                if flag:
                    card.change_status("open")
                    flag = False
                card.move_to(300 + 200 * j, y)
                gm.field[j].append(card)
            y += 40

    def return_card_to_drop_deck(self, card):
        self.drop_deck.append(card)
        card.move_to_deck()

    def restart(self):
        self.deck = []
        self.drop_deck = []
        self.create_deck()
        self.spread_cards()


if __name__ == '__main__':
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    response = main_menu()
    if response == "close game":
        pygame.quit()
    gm = Game(screen)
    deck = Deck()
    menu_button = Button(screen)
    restart_button = RestartButton()
    stats_button = StatsButton()
    stats_is_shown = False
    running = True
    card_taken = False
    card_taken_from_drop_deck = False
    one_card_taken_from_field = False
    several_cards_taken_from_field = False
    current_card = None
    current_cards = None
    old_column = None
    new_column = None
    old_coords = None
    stack = None
    rect = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                stats_is_shown = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                gm.collect_all_cards(deck)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.rect.collidepoint(event.pos):
                    response = main_menu()
                    if response == "close game":
                        gm.restart()
                        running = False
                elif restart_button.rect.collidepoint(event.pos):
                    gm.restart()
                    deck.restart()
                elif stats_button.rect.collidepoint(event.pos):
                    stats_is_shown = True
                else:
                    coords = event.pos

                    if deck.deck_rect.collidepoint(coords):
                        card_taken = True

                    elif deck.collide_point_for_drop_deck(*coords):
                        card_taken_from_drop_deck = True
                        current_card = deck.draw_card()
                        gm.moving_cards = [current_card]

                    elif response := gm.point_collide_field_card(*coords):
                        if type(response[0]) is list:
                            current_cards, old_column = response
                            if current_cards[0].is_movable:
                                several_cards_taken_from_field = True
                                gm.take_cards_from(old_column, len(current_cards))
                                gm.moving_cards = current_cards
                                old_coords = current_cards[0].rect.x, current_cards[0].rect.y
                        else:
                            current_card, old_column = response
                            if current_card.is_movable:
                                one_card_taken_from_field = True
                                gm.take_card_from(old_column)
                                gm.moving_cards = [current_card]
                                old_coords = current_card.rect.x, current_card.rect.y

            if event.type == pygame.MOUSEBUTTONUP:
                if card_taken_from_drop_deck:
                    if stack := gm.point_collide_foundation_card(*event.pos):
                        stack -= 1
                        if gm.check_foundation_cards(current_card, stack):
                            current_card.move_to(gm.foundation_rects[stack].x, gm.foundation_rects[stack].y)
                            gm.replace_card_to_foundation(current_card, stack, old_column)
                        else:
                            current_card.move_to(*old_coords)

                    elif response := gm.collide_field_rect(current_card):
                        rect, i = response
                        gm.field[i].append(current_card)
                        current_card.move_to(rect.x, rect.y)

                    elif not (new_card := gm.collide_field_card(current_card)):
                        deck.return_card_to_drop_deck(current_card)

                    else:
                        current_card.move_to_card(new_card)
                    gm.moving_cards = []
                    card_taken_from_drop_deck = False
                elif card_taken:
                    card = deck.draw_card(True)
                    gm.moving_cards = [card]
                    card.move(*event.pos)
                    card_taken = False
                    gm.moving_cards = []

                elif one_card_taken_from_field:
                    if new_column := gm.collide_field_card(current_card):
                        current_card.move_to_card(new_column)
                    gm.moving_cards = []
                    one_card_taken_from_field = False
                elif several_cards_taken_from_field:
                    move_cards_to_target(current_cards, new_column)
                    gm.moving_cards = []
                    several_cards_taken_from_field = False
        screen.fill((0, 0, 0))
        gm.show_all_field_cards()
        menu_button.draw()
        restart_button.draw()
        stats_button.draw()

        if stats_is_shown:
            gm.show_stats()

        gm.show_foundation_cards()
        gm.show_deck_cards()
        gm.show_drop_deck_cards()
        gm.show_cards()
        pygame.display.update()
        clock.tick(FPS)
