import os
import random

from mazegen.generator import MazeGenerator
from mazegen.maze_data import MazeData
from mazegen.mlx import Mlx


class MazeVisualizer:
    def __init__(self, maze_gen, settings):
        self.gui = Mlx()
        self.mlx_ptr = self.gui.mlx_init()

        self.gen_width = maze_gen.width
        self.gen_height = maze_gen.height
        self.entry = settings.get('ENTRY')
        self.exit_p = settings.get('EXIT')
        self.perfect = settings.get('PERFECT', True)
        self.seed = settings.get('SEED')

        self.tile_size = int(settings.get('TILE_SIZE', 5))
        self.show_path = True

        self.background_color = 0x0B1020
        self.floor_color = 0x151B2D
        self.wall_color = 0x7C3AED
        self.path_color = 0xFACC15
        self.start_color = 0x22C55E
        self.end_color = 0xEF4444
        self.fortytwo_bg_color = 0x2563EB
        self.fortytwo_text_color = 0xF8FAFC

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

    def _load_maze_data(self, maze_gen):
        maze_data = MazeData(maze_gen, self.entry, self.exit_p)
        self.amaze = maze_data.matrix
        self.rows = len(self.amaze)
        self.cols = len(self.amaze[0])

    def _put_pixel(self, x, y, color):
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            bytes_per_pixel = max(1, self.bpp // 8)
            index = (y * self.stride) + (x * bytes_per_pixel)
            self.img_data[index] = color & 0xFF
            self.img_data[index + 1] = (color >> 8) & 0xFF
            self.img_data[index + 2] = (color >> 16) & 0xFF
            if bytes_per_pixel >= 4:
                self.img_data[index + 3] = 0xFF

    def _fill_rect(self, x_px, y_px, width, height, color):
        for py in range(y_px, y_px + height):
            for px in range(x_px, x_px + width):
                self._put_pixel(px, py, color)

    def _draw_tile(self, cell_x, cell_y, color):
        self._fill_rect(
            cell_x * self.tile_size,
            cell_y * self.tile_size,
            self.tile_size,
            self.tile_size,
            color,
        )

    def _random_color(self):
        return random.randint(0, 0xFFFFFF)

    def _is_pathlike(self, x, y):
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.amaze[y][x] in {'P', 'S', 'E'}

    def _draw_path_cell(self, cell_x, cell_y):
        self._draw_tile(cell_x, cell_y, self.floor_color)

        if not self.show_path:
            return

        x_px = cell_x * self.tile_size
        y_px = cell_y * self.tile_size
        mid = self.tile_size // 2
        thickness = max(2, self.tile_size // 5)
        half = thickness // 2

        up = self._is_pathlike(cell_x, cell_y - 1)
        down = self._is_pathlike(cell_x, cell_y + 1)
        left = self._is_pathlike(cell_x - 1, cell_y)
        right = self._is_pathlike(cell_x + 1, cell_y)

        self._fill_rect(
            x_px + mid - half,
            y_px + mid - half,
            thickness,
            thickness,
            self.path_color,
        )

        if up:
            self._fill_rect(x_px + mid - half, y_px, thickness, mid, self.path_color)
        if down:
            self._fill_rect(
                x_px + mid - half,
                y_px + mid,
                thickness,
                self.tile_size - mid,
                self.path_color,
            )
        if left:
            self._fill_rect(x_px, y_px + mid - half, mid, thickness, self.path_color)
        if right:
            self._fill_rect(
                x_px + mid,
                y_px + mid - half,
                self.tile_size - mid,
                thickness,
                self.path_color,
            )

    def _draw_start(self, cell_x, cell_y):
        self._draw_path_cell(cell_x, cell_y)
        margin = max(2, self.tile_size // 4)
        size = self.tile_size - 2 * margin
        self._fill_rect(
            cell_x * self.tile_size + margin,
            cell_y * self.tile_size + margin,
            size,
            size,
            self.start_color,
        )

    def _draw_end(self, cell_x, cell_y):
        self._draw_path_cell(cell_x, cell_y)
        margin = max(2, self.tile_size // 4)
        x_px = cell_x * self.tile_size
        y_px = cell_y * self.tile_size
        size = self.tile_size - 2 * margin
        self._fill_rect(x_px + margin, y_px + margin, size, size, self.end_color)
        inner_margin = max(1, self.tile_size // 8)
        self._fill_rect(
            x_px + margin + inner_margin,
            y_px + margin + inner_margin,
            max(1, size - 2 * inner_margin),
            max(1, size - 2 * inner_margin),
            self.floor_color,
        )

    def _draw_forty_two(self, cell_x, cell_y):
        self._draw_tile(cell_x, cell_y, self.fortytwo_bg_color)

    def _draw_wall(self, cell_x, cell_y):
        self._draw_tile(cell_x, cell_y, self.wall_color)

    def _draw_floor(self, cell_x, cell_y):
        self._draw_tile(cell_x, cell_y, self.floor_color)

    def render(self):
        self._fill_rect(0, 0, self.win_w, self.win_h, self.background_color)

        for y in range(self.rows):
            for x in range(self.cols):
                char = self.amaze[y][x]
                if char == 'W':
                    self._draw_wall(x, y)
                elif char == '0':
                    self._draw_floor(x, y)
                elif char == 'P':
                    self._draw_path_cell(x, y)
                elif char == 'S':
                    self._draw_start(x, y)
                elif char == 'E':
                    self._draw_end(x, y)
                elif char == 'F':
                    self._draw_forty_two(x, y)
                else:
                    self._draw_floor(x, y)

        self.gui.mlx_put_image_to_window(self.mlx_ptr, self.win, self.img, 0, 0)

    def _regen(self):
        next_seed = self.seed + 1 if self.seed is not None else None
        if next_seed is not None:
            self.seed = next_seed

        maze_gen = MazeGenerator(self.gen_width, self.gen_height, next_seed)
        maze_gen.generate(self.entry, self.exit_p, self.perfect)
        self._load_maze_data(maze_gen)
        self.render()

    def _handle_key(self, keycode, _param):
        if keycode in [65307, 53]:
            os._exit(0)
        if keycode in [104, 4]:
            self.show_path = not self.show_path
            self.render()
        elif keycode in [99, 8]:
            self.wall_color = self._random_color()
            self.render()
        elif keycode in [102, 3]:
            self.fortytwo_bg_color = self._random_color()
            self.fortytwo_text_color = self._random_color()
            self.render()
        elif keycode == 32:
            self._regen()

    def run(self):
        self.gui.mlx_key_hook(self.win, self._handle_key, None)
        self.gui.mlx_hook(self.win, 17, 0, lambda *_args: os._exit(0), None)
        self.render()
        self.gui.mlx_loop(self.mlx_ptr)