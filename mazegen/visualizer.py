import mlx
import sys
import os
import random


class VizuAmaze:
    def __init__(self, maze, width=None, height=None, tile_size=32):
        self.amaze = maze
        self.h = len(maze)
        self.w = len(maze[0])
        self.tile_size = tile_size

        self.show_path = True
        self.wall_type = "wall"

        self.gui = mlx.Mlx()
        self.m_ptr = self.gui.mlx_init()
        
        self.win = self.gui.mlx_new_window(
            self.m_ptr, 
            self.w * self.tile_size, 
            self.h * self.tile_size, 
            "A-Maze-ing"
        )
        self.utils = {
            'bg': self._get_img("bg.xpm"),
            'wall': self._get_img("wall.xpm"),
            'wall_2': self._get_img("wall_2.xpm"),
            'start': self._get_img("start.xpm"),
            'end': self._get_img("end.xpm"),
            'path': self._get_img("path.xpm")
        }


    def _get_img(self, filename):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        img = self.gui.mlx_xpm_file_to_image(self.m_ptr, path)

        img_ptr = img
        img_w = self.tile_size
        img_h = self.tile_size

        if isinstance(img, (list, tuple)):
            if len(img) >= 1:
                img_ptr = img[0]
            if len(img) >= 3:
                img_w = img[1]
                img_h = img[2]

        if not img_ptr:
            print(f"Erro: {filename} não encontrado em {path}!") 
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
        for y in range(self.h):
            for x in range(self.w):
                value = self.amaze[y][x]
                x_px = x * self.tile_size
                y_px = y * self.tile_size

                self._draw_centered('bg', x_px, y_px)
                
                if value == 'W':
                    self._draw_centered(self.wall_type, x_px, y_px)
                elif value == 'S':
                    self._draw_centered('start', x_px, y_px)
                elif value == 'E':
                    self._draw_centered('end', x_px, y_px)
                elif value == 'P' and self.show_path:
                    self._draw_centered('path', x_px, y_px)
        return 0


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
        elif keycode == 99 or keycode == 8: # 99 é 'c'
            self.wall_type = 'wall_2' if self.wall_type == 'wall' else 'wall'
        elif keycode == 32: # espaco
            self.regenerate_maze()
        return 0


    def regenerate_maze(self):
        # Aqui você colocaria seu algoritmo real (DFS, Prim, etc.)
        # Para o exemplo, vamos apenas embaralhar as linhas:
        random.shuffle(self.amaze)
        print("Labirinto re-gerado!")


    def handle_close(self, param):
        self.close_app()
        return 0


    def run(self):
        self.gui.mlx_key_hook(self.win, self.handle_keys, None)
        self.gui.mlx_hook(self.win, 17, 0, self.handle_close, None)
        self.gui.mlx_hook(self.win, 33, 0, self.handle_close, None)
        self.gui.mlx_loop_hook(self.m_ptr, self.draw_amaze, None)
        self.gui.mlx_loop(self.m_ptr)


if __name__ == "__main__":
    exemplo_matriz = [
       ['W', 'W', 'W', 'W', 'W', 'W', 'W'],
        ['W', 'S', '0', '0', '0', '0', 'W'],
        ['W', 'P', '0', '0', '0', '0', 'W'],
        ['W', 'P', 'P', 'P', 'P', 'E', 'W'],
        ['W', 'W', 'W', 'W', 'W', 'W', 'W'],
    ]
    app = VizuAmaze(exemplo_matriz, tile_size=40)
    app.run()