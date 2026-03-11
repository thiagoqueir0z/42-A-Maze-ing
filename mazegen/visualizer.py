import os
import random
import time
import math
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    cast,
)
from mazegen.generator import MazeGenerator
from mazegen.maze_data import MazeData
from mazegen.mlx import Mlx


class MazeVisualizer:
    def __init__(
        self,
        maze_gen: MazeGenerator,
        settings: Mapping[str, Any],
    ) -> None:
        self.gui = Mlx()
        self.mlx_ptr = self.gui.mlx_init()

        self.gen_width = maze_gen.width
        self.gen_height = maze_gen.height
        self.entry: Tuple[int, int] = cast(
            Tuple[int, int],
            settings.get('ENTRY', (0, 0)),
        )
        self.exit_p: Tuple[int, int] = cast(
            Tuple[int, int],
            settings.get('EXIT', (self.gen_width - 1, self.gen_height - 1)),
        )
        self.perfect: bool = cast(bool, settings.get('PERFECT', True))
        self.seed: Optional[int] = cast(Optional[int], settings.get('SEED'))

        self.tile_size = int(settings.get('TILE_SIZE', 5))
        self.show_path = True

        self.background_color = 0x0B1020
        self.floor_color = 0x151B2D
        self.wall_color = 0x7C3AED
        self.path_color = 0xFACC15
        self.start_color = 0x22C55E
        self.end_color = 0xEF4444
        self.fortytwo_bg_color = 0x2563EB

        self.path_animation_enabled = True
        self.path_animation_interval = 0.02
        self.path_animation_step = 2
        self.path_reveal_index = 0
        self.path_reveal_map: Dict[Tuple[int, int], int] = {}
        self.path_reveal_max = 0
        self._last_animation_time = 0.0

        self.ui_animation_enabled = True
        self.ui_animation_interval = 0.04
        self.ui_phase = 0.0
        self.ui_phase_step = 0.35
        self._last_ui_animation_time = 0.0

        self._load_maze_data(maze_gen)

        self.win_w = self.cols * self.tile_size
        self.win_h = self.rows * self.tile_size
        self.win = self.gui.mlx_new_window(
            self.mlx_ptr,
            self.win_w,
            self.win_h,
            "A-Maze-ing",
        )

        self.img = self.gui.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr_info = self.gui.mlx_get_data_addr(self.img)
        self.bpp = addr_info[1]
        self.stride = addr_info[2]
        self.img_data = addr_info[0]

    def _load_maze_data(self, maze_gen: MazeGenerator) -> None:
        maze_data = MazeData(maze_gen, self.entry, self.exit_p)
        self.amaze = maze_data.matrix
        self.rows = len(self.amaze)
        self.cols = len(self.amaze[0])
        self._build_path_animation_map(maze_data.path)

    def _build_path_animation_map(
        self,
        path_coords: Iterable[Tuple[int, int]],
    ) -> None:
        self.path_reveal_map = {}
        idx = 0
        for px, py in path_coords:
            if (
                0 <= py < self.rows
                and 0 <= px < self.cols
                and self.amaze[py][px] == 'P'
            ):
                if (px, py) not in self.path_reveal_map:
                    self.path_reveal_map[(px, py)] = idx
                    idx += 1
        self.path_reveal_max = idx
        self.path_reveal_index = 0
        self._last_animation_time = time.time()

    def _should_draw_path_cell(self, x: int, y: int) -> bool:
        if not self.path_animation_enabled:
            return True
        reveal_pos = self.path_reveal_map.get((x, y))
        if reveal_pos is None:
            return True
        return reveal_pos < self.path_reveal_index

    def _reset_path_animation(self) -> None:
        self.path_reveal_index = 0
        self._last_animation_time = time.time()

    def _scale_color(self, color: int, factor: float) -> int:
        def clamp(channel_value: int) -> int:
            return min(255, max(0, int(channel_value * factor)))

        return (
            (clamp((color >> 16) & 0xFF) << 16)
            | (clamp((color >> 8) & 0xFF) << 8)
            | clamp(color & 0xFF)
        )

    def _pulse_value(self, phase_shift: float = 0.0) -> float:
        return (math.sin(self.ui_phase + phase_shift) + 1.0) * 0.5

    def _animated_fortytwo_color(self) -> int:
        return self._scale_color(
            self.fortytwo_bg_color,
            0.75 + 0.35 * self._pulse_value(0.8),
        )

    def _fill_rect(
        self,
        x_px: int,
        y_px: int,
        width: int,
        height: int,
        color: int,
    ) -> None:
        if width <= 0 or height <= 0:
            return

        x0 = max(0, x_px)
        y0 = max(0, y_px)
        x1 = min(self.win_w, x_px + width)
        y1 = min(self.win_h, y_px + height)

        if x0 >= x1 or y0 >= y1:
            return

        bytes_per_pixel = max(1, self.bpp // 8)
        pixel = bytearray(bytes_per_pixel)
        pixel[0] = color & 0xFF
        if bytes_per_pixel >= 2:
            pixel[1] = (color >> 8) & 0xFF
        if bytes_per_pixel >= 3:
            pixel[2] = (color >> 16) & 0xFF
        if bytes_per_pixel >= 4:
            pixel[3] = 0xFF

        span_width = x1 - x0
        row_bytes = bytes(pixel) * span_width

        for py in range(y0, y1):
            row_start = (py * self.stride) + (x0 * bytes_per_pixel)
            row_end = row_start + len(row_bytes)
            self.img_data[row_start:row_end] = row_bytes

    def _draw_tile(self, cell_x: int, cell_y: int, color: int) -> None:
        self._fill_rect(
            cell_x * self.tile_size,
            cell_y * self.tile_size,
            self.tile_size,
            self.tile_size,
            color,
        )

    def _random_color(self) -> int:
        return random.randint(0, 0xFFFFFF)

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

    def render(self) -> None:
        draw: Dict[str, Callable[[int, int], None]] = {
            'W': self._draw_wall,
            'S': self._draw_start,
            'E': self._draw_end,
        }
        ft_color = self._animated_fortytwo_color()
        for y in range(self.rows):
            for x in range(self.cols):
                char = self.amaze[y][x]
                if char == 'F':
                    self._draw_tile(x, y, ft_color)
                elif char in draw:
                    self._draw_tile(x, y, self.background_color)
                    draw[char](x, y)
                elif char == 'P':
                    self._draw_tile(x, y, self.background_color)
                    if self._should_draw_path_cell(x, y):
                        self._draw_path_cell(x, y)
                    else:
                        self._draw_tile(x, y, self.floor_color)
                else:
                    self._draw_tile(x, y, self.floor_color)
        self.gui.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win,
            self.img,
            0,
            0,
        )

    def _loop_tick(self, _param: Any) -> None:
        now = time.time()
        should_render = False

        if (
            self.ui_animation_enabled
            and now - self._last_ui_animation_time
            >= self.ui_animation_interval
        ):
            self._last_ui_animation_time = now
            self.ui_phase += self.ui_phase_step
            should_render = True

        if (
            self.show_path
            and self.path_animation_enabled
            and self.path_reveal_index < self.path_reveal_max
        ):
            if now - self._last_animation_time >= self.path_animation_interval:
                self._last_animation_time = now
                self.path_reveal_index = min(
                    self.path_reveal_max,
                    self.path_reveal_index + self.path_animation_step,
                )
                should_render = True

        if should_render:
            self.render()

    def _regen(self) -> None:
        if self.seed is not None:
            self.seed += 1
        maze_gen = MazeGenerator(self.gen_width, self.gen_height, self.seed)
        maze_gen.generate(self.entry, self.exit_p, self.perfect)
        self._load_maze_data(maze_gen)
        self.render()

    def _handle_key(self, keycode: int, _param: Any) -> None:
        if keycode in [65307, 53]:
            os._exit(0)
        if keycode in [104, 4]:
            self.show_path = not self.show_path
            if self.show_path:
                self._reset_path_animation()
            self.render()
        elif keycode in [99, 8]:
            self.wall_color = self._random_color()
            self.render()
        elif keycode in [102, 3]:
            self.fortytwo_bg_color = self._random_color()
            self.render()
        elif keycode == 32:
            self._regen()

    def _handle_close(self, _param: Any) -> None:
        os._exit(0)

    def run(self) -> None:
        self.gui.mlx_key_hook(self.win, self._handle_key, None)
        self.gui.mlx_hook(self.win, 17, 0, self._handle_close, None)
        self.gui.mlx_loop_hook(self.mlx_ptr, self._loop_tick, None)
        self.render()
        self.gui.mlx_loop(self.mlx_ptr)
