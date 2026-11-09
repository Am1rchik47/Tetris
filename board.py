from settings import GRID_HEIGHT, GRID_WIDTH


class Board:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        # 0 - пустая клетка, иначе цвет замороженного блока
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def fits(self, piece):
        # Фигура помещается, если все её клетки в поле и не заняты
        for x, y in piece.cells():
            if x < 0 or x >= self.width or y >= self.height:
                return False
            if y >= 0 and self.grid[y][x] != 0:
                return False
        return True

    def lock(self, piece):
        # Заморозка фигуры
        for x, y in piece.cells():
            if y >= 0:
                self.grid[y][x] = piece.color

    def clear_lines(self):
        # Убирает заполненные линии, сдвигает остальные вниз, возвращает их число
        remaining = [row for row in self.grid if not all(cell != 0 for cell in row)]
        cleared = self.height - len(remaining)
        empty_rows = [[0 for _ in range(self.width)] for _ in range(cleared)]
        self.grid = empty_rows + remaining
        return cleared
