import mlx
import sys
import os

class VizuAmaze:
    def __init__(self, maze, width, height):
        self.amaze = maze
        self.w = width
        self.h = height
        self.tile_size = 40

        self.gui = mlx.Mlx()
        self.m_ptr = self.gui.mlx_init()
        
        self.win = self.gui.mlx_new_window(
            self.m_ptr, self.w * self.tile_size, self.h * self.tile_size, "A-Maze-ing"
        )
        self.utils = {
            'wall': self._get_img("wall.xpm"),
            'start': self._get_img("path_start.xpm"),
            'end': self._get_img("path_end.xpm")
        }
    def _get_img(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        img_ptr = self.gui.mlx_xpm_file_to_image(self.m_ptr, path)
        
        if isinstance(img_ptr, (list, tuple)):
            img_ptr = img_ptr[0]
            
        if not img_ptr:
            print(f"Erro: {filename} não encontrado!")
            sys.exit(1)
        return img_ptr

    def draw_amaze(self, param=None):
        for y in range(self.h):
            for x in range(self.w):
                value = self.amaze[y][x]

                if value > 0:
                    x_pixel = x * self.tile_size
                    y_pixel = y * self.tile_size

                    self.gui.mlx_put_image_to_window(
                        self.m_ptr, self.win, self.wall_ptr, x_pixel, y_pixel
                    )
        return 0

    def handle_keys(self, keycode, param):
        if keycode == 65307:
            import os
            os._exit(0)
        return 0

    def run(self):
        self.gui.mlx_key_hook(self.win, self.handle_keys, None)
        self.gui.mlx_loop_hook(self.m_ptr, self.draw_amaze, None)
        self.gui.mlx_loop(self.m_ptr)

# --- Exemplo de como chamar ---
if __name__ == "__main__":
    exemplo_matriz = [
       ['W', 'W', 'W', 'W', 'W'],
        ['W', 'S', 'P', '0', 'W'],
        ['W', '0', 'P', '0', 'W'],
        ['W', '0', 'P', 'E', 'W'],
        ['W', 'W', 'W', 'W', 'W']
    ]
    app = VizuAmaze(exemplo_matriz, 5, 5)
    app.run()