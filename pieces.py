import random
from dataclasses import dataclass, replace

from settings import GRID_WIDTH, PIECE_COLORS

# Базовые формы: размер квадрата, в который вписана фигура, и клетки (x, y)
SHAPES = {
    "I": (4, [(0, 1), (1, 1), (2, 1), (3, 1)]),
    "O": (2, [(0, 0), (1, 0), (0, 1), (1, 1)]),
    "T": (3, [(1, 0), (0, 1), (1, 1), (2, 1)]),
    "S": (3, [(1, 0), (2, 0), (0, 1), (1, 1)]),
    "Z": (3, [(0, 0), (1, 0), (1, 1), (2, 1)]),
    "J": (3, [(0, 0), (0, 1), (1, 1), (2, 1)]),
    "L": (3, [(2, 0), (0, 1), (1, 1), (2, 1)]),
}


def _rotate_clockwise(cells, size):
    # Поворот клеток по часовой стрелке внутри квадрата size x size
    return [(size - 1 - y, x) for x, y in cells]


def _build_rotations(size, cells):
    rotations = [cells]
    for _ in range(3):
        rotations.append(_rotate_clockwise(rotations[-1], size))
    return rotations


# Все 4 положения каждой фигуры
ROTATIONS = {
    kind: _build_rotations(size, cells) for kind, (size, cells) in SHAPES.items()
}


@dataclass(frozen=True)
class Piece:
    kind: str
    x: int
    y: int = 0
    rotation: int = 0

    @property
    def color(self):
        return PIECE_COLORS[self.kind]

    def cells(self):
        # Клетки фигуры в координатах поля
        return [
            (self.x + cx, self.y + cy) for cx, cy in ROTATIONS[self.kind][self.rotation]
        ]

    def moved(self, dx, dy):
        return replace(self, x=self.x + dx, y=self.y + dy)

    def rotated(self):
        return replace(self, rotation=(self.rotation + 1) % 4)


def spawn(kind):
    # Новая фигура появляется сверху по центру
    size = SHAPES[kind][0]
    return Piece(kind, x=(GRID_WIDTH - size) // 2)


class PieceBag:
    # "Мешок": все 7 фигур выпадают по разу, потом мешок перемешивается заново
    def __init__(self):
        self._bag = []

    def next_kind(self):
        if not self._bag:
            self._bag = list(SHAPES)
            random.shuffle(self._bag)
        return self._bag.pop()
