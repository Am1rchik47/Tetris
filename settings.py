# Настройки игры

# Сетка
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Окно: игровое поле + боковая панель
FIELD_WIDTH = GRID_WIDTH * CELL_SIZE
FIELD_HEIGHT = GRID_HEIGHT * CELL_SIZE
PANEL_WIDTH = 200
WINDOW_WIDTH = FIELD_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = FIELD_HEIGHT

FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
PANEL_COLOR = (25, 25, 25)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (200, 0, 255)
ORANGE = (255, 140, 0)

# Цвет каждой фигуры
PIECE_COLORS = {
    "I": CYAN,
    "O": YELLOW,
    "T": MAGENTA,
    "S": GREEN,
    "Z": RED,
    "J": BLUE,
    "L": ORANGE,
}

# Время (в миллисекундах)
BASE_INTERVAL = 500  # начальная скорость падения
MIN_INTERVAL = 100  # самая быстрая скорость
LEVEL_SPEEDUP = 40  # на сколько ускоряется падение за уровень
LINES_PER_LEVEL = 10  # сколько линий нужно для нового уровня
REPEAT_DELAY = 170  # задержка перед автоповтором зажатой клавиши
REPEAT_INTERVAL = 50  # интервал автоповтора

# Очки за 1, 2, 3 и 4 линии одновременно (умножаются на уровень + 1)
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# Файл, где хранится рекорд (рядом с игрой)
HIGHSCORE_FILE = "highscore.txt"
