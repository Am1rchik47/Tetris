import os
import sys

import pygame
from board import Board
from pieces import ROTATIONS, PieceBag, spawn
from settings import (
    BASE_INTERVAL,
    BLACK,
    CELL_SIZE,
    FIELD_HEIGHT,
    FIELD_WIDTH,
    FPS,
    GRAY,
    HIGHSCORE_FILE,
    LEVEL_SPEEDUP,
    LINE_SCORES,
    LINES_PER_LEVEL,
    MIN_INTERVAL,
    PANEL_COLOR,
    PANEL_WIDTH,
    PIECE_COLORS,
    REPEAT_DELAY,
    REPEAT_INTERVAL,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)

HIGHSCORE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), HIGHSCORE_FILE
)

# Управление: направление (dx, dy) -> клавиши
MOVE_KEYS = {
    (-1, 0): (pygame.K_a, pygame.K_LEFT),
    (1, 0): (pygame.K_d, pygame.K_RIGHT),
    (0, 1): (pygame.K_s, pygame.K_DOWN),
}
ROTATE_KEYS = (pygame.K_w, pygame.K_UP)
DROP_KEY = pygame.K_SPACE

HINTS = ["A/D - движение", "S - вниз", "W - поворот", "Пробел - сброс", "P - пауза"]


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")

        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 22)
        self.big_font = pygame.font.Font(None, 38)

        # Счет и рекорд
        self.highscore = self.load_highscore()
        self.saved_highscore = self.highscore
        self.reset()

    # ----- Состояние игры -----

    def reset(self):
        self.board = Board()
        self.bag = PieceBag()
        self.next_kind = self.bag.next_kind()
        self.piece = None
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.held = {}  # зажатые клавиши движения: направление -> время следующего повтора
        self.spawn_piece()
        self.last_step = pygame.time.get_ticks()

    @property
    def level(self):
        return self.lines // LINES_PER_LEVEL

    @property
    def interval(self):
        # Чем выше уровень, тем быстрее падает фигура
        return max(MIN_INTERVAL, BASE_INTERVAL - self.level * LEVEL_SPEEDUP)

    def spawn_piece(self):
        self.piece = spawn(self.next_kind)
        self.next_kind = self.bag.next_kind()
        if not self.board.fits(self.piece):
            self.game_over = True
            self.save_highscore()

    def move(self, dx, dy):
        moved = self.piece.moved(dx, dy)
        if self.board.fits(moved):
            self.piece = moved
            return True
        return False

    def rotate(self):
        rotated = self.piece.rotated()
        # Если у стены не хватает места, пробуем сдвинуть фигуру в сторону
        for dx in (0, -1, 1, -2, 2):
            candidate = rotated.moved(dx, 0)
            if self.board.fits(candidate):
                self.piece = candidate
                return

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        self.board.lock(self.piece)
        cleared = self.board.clear_lines()
        if cleared:
            self.score += LINE_SCORES[cleared] * (self.level + 1)
            self.lines += cleared
            if self.score > self.highscore:
                self.highscore = self.score
        self.spawn_piece()

    def update(self, now):
        # Резкая анимация падения
        if now - self.last_step >= self.interval:
            if not self.move(0, 1):
                self.lock_piece()
            self.last_step = now

    # ----- Рекорд -----

    @staticmethod
    def load_highscore():
        try:
            with open(HIGHSCORE_PATH) as file:
                return int(file.read().strip())
        except (OSError, ValueError):
            return 0

    def save_highscore(self):
        if self.highscore <= self.saved_highscore:
            return
        try:
            with open(HIGHSCORE_PATH, "w") as file:
                file.write(str(self.highscore))
            self.saved_highscore = self.highscore
        except OSError:
            pass

    # ----- Ввод -----

    def quit_game(self):
        print(f"Счет: {self.score}")
        print(f"Рекорд: {self.highscore}")
        self.save_highscore()
        pygame.quit()
        sys.exit()

    def handle_events(self, now):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_r and self.game_over:
                self.reset()
            elif event.key == pygame.K_p and not self.game_over:
                self.paused = not self.paused
                self.held.clear()
                self.last_step = now
            elif not self.game_over and not self.paused:
                self.handle_game_key(event.key, now)

    def handle_game_key(self, key, now):
        for direction, keys in MOVE_KEYS.items():
            if key in keys:
                self.move(*direction)
                self.held[direction] = now + REPEAT_DELAY
        if key in ROTATE_KEYS:
            self.rotate()
        elif key == DROP_KEY:
            self.hard_drop()

    def handle_held_keys(self, now):
        # Автоповтор, пока клавиша движения зажата
        pressed = pygame.key.get_pressed()
        for direction, keys in MOVE_KEYS.items():
            if direction not in self.held:
                continue
            if not any(pressed[key] for key in keys):
                del self.held[direction]
            elif now >= self.held[direction]:
                self.move(*direction)
                self.held[direction] = now + REPEAT_INTERVAL

    # ----- Отрисовка -----

    def draw_text(self, text, font, color, x, y, center=False):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.window.blit(surface, rect)

    def draw_cell(self, x_cell, y_cell, color):
        pygame.draw.rect(
            self.window,
            color,
            (x_cell * CELL_SIZE, y_cell * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )

    def draw_field(self):
        self.window.fill(BLACK)

        # Замороженные блоки
        for row_idx, row in enumerate(self.board.grid):
            for col_idx, cell_color in enumerate(row):
                if cell_color != 0:
                    self.draw_cell(col_idx, row_idx, cell_color)

        # Текущая фигура
        if not self.game_over:
            for x, y in self.piece.cells():
                self.draw_cell(x, y, self.piece.color)

        # Линии сетки (черные - разделяют блоки)
        for x in range(0, FIELD_WIDTH, CELL_SIZE):
            pygame.draw.line(self.window, BLACK, (x, 0), (x, FIELD_HEIGHT))
        for y in range(0, FIELD_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.window, BLACK, (0, y), (FIELD_WIDTH, y))

    def draw_next_piece(self, left, top):
        cells = ROTATIONS[self.next_kind][0]
        color = PIECE_COLORS[self.next_kind]
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        # Центрируем фигуру в области 4 x 2 клетки
        offset_x = left + (4 - (max_x - min_x + 1)) * CELL_SIZE // 2
        offset_y = top + (2 - (max_y - min_y + 1)) * CELL_SIZE // 2
        for x, y in cells:
            rect = (
                offset_x + (x - min_x) * CELL_SIZE,
                offset_y + (y - min_y) * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(self.window, color, rect)
            pygame.draw.rect(self.window, BLACK, rect, 1)

    def draw_panel(self):
        pygame.draw.rect(
            self.window, PANEL_COLOR, (FIELD_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        )
        pygame.draw.line(
            self.window, GRAY, (FIELD_WIDTH, 0), (FIELD_WIDTH, WINDOW_HEIGHT)
        )

        left = FIELD_WIDTH + 20
        stats = [
            ("Счет", self.score),
            ("Рекорд", self.highscore),
            ("Линии", self.lines),
            ("Уровень", self.level + 1),
        ]
        top = 20
        for label, value in stats:
            self.draw_text(label, self.small_font, GRAY, left, top)
            self.draw_text(str(value), self.font, WHITE, left, top + 22)
            top += 65

        self.draw_text("Следующая", self.small_font, GRAY, left, top + 10)
        self.draw_next_piece(left, top + 40)

        hint_top = WINDOW_HEIGHT - 20 - len(HINTS) * 22
        for i, hint in enumerate(HINTS):
            self.draw_text(hint, self.small_font, GRAY, left, hint_top + i * 22)

    def draw_overlay(self, title, hint):
        shade = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        self.window.blit(shade, (0, 0))
        center_x = FIELD_WIDTH // 2
        self.draw_text(
            title, self.big_font, WHITE, center_x, FIELD_HEIGHT // 2 - 20, center=True
        )
        self.draw_text(
            hint, self.small_font, GRAY, center_x, FIELD_HEIGHT // 2 + 20, center=True
        )

    def draw(self):
        self.draw_field()
        self.draw_panel()
        if self.game_over:
            self.draw_overlay("Игра окончена", "R - играть снова")
        elif self.paused:
            self.draw_overlay("Пауза", "P - продолжить")

    # ----- Главный цикл -----

    def run(self):
        while True:
            now = pygame.time.get_ticks()
            self.handle_events(now)
            if not self.game_over and not self.paused:
                self.handle_held_keys(now)
                self.update(now)
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
