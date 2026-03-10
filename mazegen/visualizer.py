from mazegen import mlx
import sys
import os
from mazegen.generator import MazeGenerator
from mazegen.maze_data import MazeData


class MazeVisualizer:
    def __init__(self, maze, settings):
        self.tile_size = int(settings.get('TILE_SIZE', 32))

        if isinstance(maze, MazeGenerator):
            self.seed = settings.get('SEED')
            self.perfect = settings.get('PERFECT', False)
            self.entry = settings.get('ENTRY', (0, 0))
            self.exit_p = settings.get(
                'EXIT',
                (maze.width - 1, maze.height - 1)
            )
            self.gen_width = maze.width
            self.gen_height = maze.height
            maze_data = MazeData(maze, self.entry, self.exit_p)
            self.amaze = maze_data.matrix
            self.path_cells = maze_data.path
        else:
            self.seed = settings.get('SEED')
            self.perfect = settings.get('PERFECT', False)
            self.amaze = maze
            self.h = len(maze)
            self.w = len(maze[0])
            self.gen_width = (self.w - 1) // 2 if self.w % 2 == 1 else self.w
            self.gen_height = (self.h - 1) // 2 if self.h % 2 == 1 else self.h
            self.entry = settings.get('ENTRY', (0, 0))
            self.exit_p = settings.get(
                'EXIT',
                (self.gen_width - 1, self.gen_height - 1)
            )
            self.path_cells = None

        self.h = len(self.amaze)
        self.w = len(self.amaze[0])

        self.show_path = True
        self.wall_index = 0
        self.needs_redraw = True
        if self.path_cells is None:
            self.path_cells = self._build_path_list()

        self.gui = mlx.Mlx()
        self.m_ptr = self.gui.mlx_init()
        
        self.win = self.gui.mlx_new_window(
            self.m_ptr, 
            int(self.w * self.tile_size), 
            int(self.h * self.tile_size),
            "A-Maze-ing"
        )
        self.utils = {
            'bg': self._get_img("bg.xpm"),
            'wall_h': self._get_img("wall_h.xpm"),
            'wall_v': self._get_img("wall_v.xpm"),
            'wall_c': self._get_img("wall_c.xpm"),
            'wall': self._get_img("wall.xpm"),
            'start': self._get_img("start.xpm"),
            'end': self._get_img("end.xpm"),
            'path': self._get_img("path.xpm")
        }


    def _build_path_list(self):
        """Constrói lista ordenada de células do caminho (S -> E)"""
        path = []
        for y in range(self.h):
            for x in range(self.w):
                if self.amaze[y][x] == 'P':
                    path.append((x, y))
        return path


    def _get_img(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            project_root = os.path.dirname(base_dir)
            alt_path = os.path.join(project_root, 'assets', filename)
            if os.path.exists(alt_path):
                path = alt_path
        img = self.gui.mlx_xpm_file_to_image(self.m_ptr, path)

        img_ptr = img
        img_w = self.tile_size
        img_h = self.tile_size

        try:
            if isinstance(img, (list, tuple)):
                if len(img) >= 1:
                    img_ptr = img[0]
                if len(img) >= 3:
                    img_w = img[1]
                    img_h = img[2]

            if not img_ptr:
                print(f"Erro: {filename} não encontrado em {path}!") 
                sys.exit(1)         
        except (IndexError, TypeError, ValueError) as e:
            print(f"Erro ao processar {filename}: {e}")
            sys.exit(1)
        return {
            'ptr': img_ptr,
            'w': img_w,
            'h': img_h,
        }


    def _draw_centered(self, sprite_key, tile_x, tile_y):
        sprite = self.utils[sprite_key]
        off_x = (self.tile_size - sprite['w']) // 2
        off_y = (self.tile_size - sprite['h']) // 2
        self.gui.mlx_put_image_to_window(
            self.m_ptr,
            self.win,
            sprite['ptr'],
            tile_x + off_x,
            tile_y + off_y,
        )


    def draw_amaze(self, param=None):
        if not self.needs_redraw:
            return 0
            
        for y in range(self.h):
            for x in range(self.w):
                x_px = x * self.tile_size
                y_px = y * self.tile_size

                self._draw_centered('bg', x_px, y_px)
                
                value = self.amaze[y][x]
                if value == 'W':
                    if self.wall_index == 0:
                        sprite_conectado = self._get_wall_sprite(x, y)
                        self._draw_centered(sprite_conectado, x_px, y_px)
                    else:
                        self._draw_centered('wall', x_px, y_px)
                elif value == 'P' and self.show_path:
                    self._draw_centered('path', x_px, y_px)
                elif value == 'S':
                    self._draw_centered('start', x_px, y_px)
                elif value == 'E':
                    self._draw_centered('end', x_px, y_px)
        
        self.needs_redraw = False
        return 0 


    def _get_wall_sprite(self, x, y):
    # Verifica vizinhos (W)
        up = y > 0 and self.amaze[y-1][x] == 'W'
        down = y < self.h - 1 and self.amaze[y+1][x] == 'W'
        left = x > 0 and self.amaze[y][x-1] == 'W'
        right = x < self.w - 1 and self.amaze[y][x+1] == 'W'

        # 1. Se for uma linha RETA Vertical (tem em cima/baixo mas não nas laterais)
        if (up or down) and not (left or right):
            return 'wall_v'
        
        # 2. Se for uma linha RETA Horizontal (tem nas laterais mas não em cima/baixo)
        if (left or right) and not (up or down):
            return 'wall_h'
        
        # 3. Se tiver vizinhos em AMBAS as direções (quina ou cruzamento)
        if (up or down) and (left or right):
            return 'wall_c' # Usa o tile com a cruz '+'

        # 4. Caso isolado (uma parede solta)
        return 'wall' # Um ponto ou cruz pequena padrão

    def close_app(self):
        try:
            self.gui.mlx_loop_exit(self.m_ptr)
            self.gui.mlx_destroy_window(self.m_ptr, self.win)
        except Exception:
            pass
        os._exit(0)


    def handle_keys(self, keycode, param):
        print(f"Tecla pressionada: {keycode}")

        if keycode == 65307:
            self.close_app()
        elif keycode == 104 or keycode == 4: # 104 é 'h'
            self.show_path = not self.show_path
            self.needs_redraw = True
        elif keycode == 99 or keycode == 8: # 99 é 'c'
            self.wall_index = (self.wall_index + 1) % 2
            print(f"Wall style: {self.wall_index + 1}/2")
            self.needs_redraw = True
        elif keycode == 32: # espaco
            self.regenerate_maze()
        return 0


    def regenerate_maze(self):
        gen = MazeGenerator(self.gen_width, self.gen_height, self.seed)
        gen.generate(self.entry, self.exit_p, self.perfect)
        maze_data = MazeData(gen, self.entry, self.exit_p)
        self.amaze = maze_data.matrix
        self.path_cells = maze_data.path
        self.needs_redraw = True


    def handle_close(self, param):
        self.close_app()
        return 0


    def run(self):
        
        self.gui.mlx_key_hook(self.win, self.handle_keys, None)
        self.gui.mlx_hook(self.win, 17, 0, self.handle_close, None)
        self.gui.mlx_hook(self.win, 33, 0, self.handle_close, None)
        self.gui.mlx_loop_hook(self.m_ptr, self.draw_amaze, None)
        self.gui.mlx_loop(self.m_ptr)
