import os
from typing import Any, Callable, Dict, Mapping, Optional, Tuple, cast

from mazegen.animator import Animator
from mazegen.generator import MazeGenerator
from mazegen.maze_data import MazeData
from mazegen.mlx import Mlx
from mazegen.renderer import Renderer
from mazegen.tile_drawer import TileDrawer


class MazeVisualizer(Renderer, TileDrawer, Animator):
    """
    Handle the graphical representation and user interaction of the maze.

    This class manages the MiniLibX (MLX) window, renders maze tiles,
    controls path animations, and responds to keyboard events for
    regeneration or visual customization.
    """

    def __init__(
        self,
        maze_gen: MazeGenerator,
        settings: Mapping[str, Any],
    ) -> None:
        """
        Initialize the visualizer with the provided generator and settings.

        Args:
            maze_gen: An instance of MazeGenerator containing the maze logic.
            settings: A mapping containing configuration keys such as
                'TILE_SIZE', 'ENTRY', 'EXIT', 'PERFECT', and 'SEED'.
        """
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
        """
        Process raw generator data into a visual matrix format.

        Args:
            maze_gen: The maze generator containing the logical structure.
        """
        maze_data = MazeData(maze_gen, self.entry, self.exit_p)
        self.amaze = maze_data.matrix
        self.rows = len(self.amaze)
        self.cols = len(self.amaze[0])
        self._build_path_animation_map(maze_data.path)

    def render(self) -> None:
        """
        Draw the current maze state to the image buffer and display the window.

        Iterates through the maze matrix, drawing walls,
        floors, entry/exit points,
        and the solution path if active, using static or animated colors.
        """
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

    def _regen(self) -> None:
        """Regenerate the maze by incrementing the seed
        and updating the data."""
        if self.seed is not None:
            self.seed += 1
        maze_gen = MazeGenerator(self.gen_width, self.gen_height, self.seed)
        maze_gen.generate(self.entry, self.exit_p, self.perfect)
        self._load_maze_data(maze_gen)
        self.render()

    def _handle_key(self, keycode: int, _param: Any) -> None:
        """
        Handle user keyboard inputs.

        Shortcuts:
            - ESC: Exit the application.
            - H: Toggle path visibility.
            - C: Randomize wall color.
            - F: Randomize highlight color.
            - Space: Regenerate the maze.
        """
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
        """Terminate the program cleanly when the window is closed."""
        os._exit(0)

    def run(self) -> None:
        """
        Start the MiniLibX main event loop.

        Configures keyboard hooks, window closure hooks, and the loop hook
        used for constant UI and path animations.
        """
        self.gui.mlx_key_hook(self.win, self._handle_key, None)
        self.gui.mlx_hook(self.win, 17, 0, self._handle_close, None)
        self.gui.mlx_loop_hook(self.mlx_ptr, self._loop_tick, None)
        self.render()
        self.gui.mlx_loop(self.mlx_ptr)
