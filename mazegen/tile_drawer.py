from typing import Tuple


class TileDrawerMixin:
    """Draws individual maze cell types (floor, wall, path, start, end)."""

    def _is_pathlike(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.amaze[y][x] in {'P', 'S', 'E'}

    def _is_wall(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.amaze[y][x] == 'W'

    def _draw_path_cell(self, cell_x: int, cell_y: int) -> None:
        self._draw_tile(cell_x, cell_y, self.floor_color)
        if not self.show_path:
            return
        x_px, y_px = cell_x * self.tile_size, cell_y * self.tile_size
        mid = self.tile_size // 2
        t = max(2, self.tile_size // 10)
        h = t // 2
        self._fill_rect(x_px + mid - h, y_px + mid - h, t, t, self.path_color)
        if self._is_pathlike(cell_x, cell_y - 1):
            self._fill_rect(x_px + mid - h, y_px, t, mid, self.path_color)
        if self._is_pathlike(cell_x, cell_y + 1):
            self._fill_rect(
                x_px + mid - h,
                y_px + mid,
                t,
                self.tile_size - mid,
                self.path_color,
            )
        if self._is_pathlike(cell_x - 1, cell_y):
            self._fill_rect(x_px, y_px + mid - h, mid, t, self.path_color)
        if self._is_pathlike(cell_x + 1, cell_y):
            self._fill_rect(
                x_px + mid,
                y_px + mid - h,
                self.tile_size - mid,
                t,
                self.path_color,
            )

    def _pulse_marker(self, color: int, phase_shift: float) -> Tuple[int, int]:
        pulse = self._pulse_value(phase_shift)
        margin = max(1, self.tile_size // 6 - (1 if pulse > 0.55 else 0))
        return margin, self._scale_color(color, 0.85 + 0.25 * pulse)

    def _draw_start(self, cell_x: int, cell_y: int) -> None:
        self._draw_path_cell(cell_x, cell_y)
        margin, color = self._pulse_marker(self.start_color, 0.0)
        size = self.tile_size - 2 * margin
        self._fill_rect(
            cell_x * self.tile_size + margin,
            cell_y * self.tile_size + margin,
            size,
            size,
            color,
        )

    def _draw_end(self, cell_x: int, cell_y: int) -> None:
        self._draw_path_cell(cell_x, cell_y)
        margin, color = self._pulse_marker(self.end_color, 1.3)
        x_px, y_px = cell_x * self.tile_size, cell_y * self.tile_size
        size = self.tile_size - 2 * margin
        self._fill_rect(x_px + margin, y_px + margin, size, size, color)
        im = max(1, self.tile_size // 8)
        self._fill_rect(
            x_px + margin + im,
            y_px + margin + im,
            max(1, size - 2 * im),
            max(1, size - 2 * im),
            self.floor_color,
        )

    def _draw_wall(self, cell_x: int, cell_y: int) -> None:
        self._draw_tile(cell_x, cell_y, self.background_color)
        x_px, y_px = cell_x * self.tile_size, cell_y * self.tile_size
        mid = self.tile_size // 2
        t = max(1, self.tile_size // 8)
        h = t // 2
        self._fill_rect(x_px + mid - h, y_px + mid - h, t, t, self.wall_color)
        if self._is_wall(cell_x, cell_y - 1):
            self._fill_rect(x_px + mid - h, y_px, t, mid, self.wall_color)
        if self._is_wall(cell_x, cell_y + 1):
            self._fill_rect(
                x_px + mid - h,
                y_px + mid,
                t,
                self.tile_size - mid,
                self.wall_color,
            )
        if self._is_wall(cell_x - 1, cell_y):
            self._fill_rect(x_px, y_px + mid - h, mid, t, self.wall_color)
        if self._is_wall(cell_x + 1, cell_y):
            self._fill_rect(
                x_px + mid,
                y_px + mid - h,
                self.tile_size - mid,
                t,
                self.wall_color,
            )
