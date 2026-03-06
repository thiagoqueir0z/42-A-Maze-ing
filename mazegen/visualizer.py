import mlx
import sys
import os
from mazegen.parser import parse_config
import random


class VizuAmaze:
    def __init__(self, maze, tile_size=32, config_path=None):
        self.amaze = maze
        self.h = len(maze)
        self.w = len(maze[0])

        if config_path:
            try:
                config = parse_config(config_path)
                self.tile_size = int(config.get('TILE_SIZE', tile_size))
            except Exception:
                self.tile_size = tile_size
        else:
            self.tile_size = tile_size

        self.show_path = True
        self.wall_index = 0
        self.path_reveal_index = 0
        self.reveal_speed = 10
        self.frame_counter = 0
        self.path_cells = self._build_path_list()
        self.footer = 80

        self.gui = mlx.Mlx()
        self.m_ptr = self.gui.mlx_init()
        
        self.win = self.gui.mlx_new_window(
            self.m_ptr, 
            self.w * self.tile_size, 
            self.h * self.tile_size + self.footer,
            "A-Maze-ing"
        )
        self.utils = {
            'bg': self._get_img("bg.xpm"),
            'wall': self._get_img("wall.xpm"),
            'wall_2': self._get_img("wall_2.xpm"),
            # 'wall_3': self._get_img("wall_3.xpm"),
            # 'wall_4': self._get_img("wall_4.xpm"),
            # 'wall_5': self._get_img("wall_5.xpm"),
            # 'wall_6': self._get_img("wall_6.xpm"),
            # 'wall_7': self._get_img("wall_7.xpm"),
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
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        img = self.gui.mlx_xpm_file_to_image(self.m_ptr, path)

        img_ptr = img
        img_w = self.tile_size
        img_h = self.tile_size

        try:
            if isinstance(img, (list, tuple)):
                if len(img) >= 1:      # mlx_string_put usa ~6 pixels por caractere
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
        self.frame_counter += 1
        if self.frame_counter % self.reveal_speed == 0:
            if self.path_reveal_index < len(self.path_cells):
                self.path_reveal_index += 1

        for y in range(self.h):
            for x in range(self.w):
                value = self.amaze[y][x]
                x_px = x * self.tile_size
                y_px = y * self.tile_size

                self._draw_centered('bg', x_px, y_px)
                
                if value == 'W':
                    sprite_conectado = self._get_wall_sprite(x, y)
                    self._draw_centered(sprite_conectado, x_px, y_px)
                elif value == 'S':
                    self._draw_centered('start', x_px, y_px)
                elif value == 'E':
                    self._draw_centered('end', x_px, y_px)
                elif value == 'P' and self.show_path:
                    # Só desenha se já foi revelado
                    cell_index = self._get_cell_reveal_order(x, y)
                    if cell_index < self.path_reveal_index:
                        self._draw_centered('path', x_px, y_px)
        
        self._draw_help_text()
        return 0
    
    def _get_wall_sprite(self, x, y):
    # Verifica se os vizinhos são paredes ('W')
        up = y > 0 and self.amaze[y-1][x] == 'W'
        down = y < self.h - 1 and self.amaze[y+1][x] == 'W'
        left = x > 0 and self.amaze[y][x-1] == 'W'
        right = x < self.w - 1 and self.amaze[y][x+1] == 'W'

        # Se tem vizinho na horizontal mas não na vertical
        if (left or right) and not (up or down):
            return 'wall_h'
        # Se tem vizinho na vertical mas não na horizontal
        if (up or down) and not (left or right):
            return 'wall_v'
        # Se for uma quina ou cruzamento
        return 'wall_c'

    def _get_cell_reveal_order(self, x, y):
        """Retorna índice de revelação da célula (ou infinito se não for caminho)"""
        try:
            return self.path_cells.index((x, y))
        except ValueError:
            return float('inf')

    def _draw_help_text(self):
        """Desenha legenda de comandos compacta"""
        footer_text = "   H: path C: color " \
        "R: reset SPACE: regen " \
        "ESC: quit"
        text_x = 10
        text_y = self.h * self.tile_size + 12
        self.gui.mlx_string_put(
            self.m_ptr,
            self.win,
            text_x,
            text_y,
            0xFFFFFF,
            footer_text
        )


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
            self.wall_index = (self.wall_index + 1) % 7
            print(f"Wall color: {self.wall_index + 1}/7")
        elif keycode == 32: # espaco
            self.regenerate_maze()
        elif keycode == 114:  # 'r' = reset animação
            self.path_reveal_index = 0
            self.frame_counter = 0
        return 0


    def regenerate_maze(self):
        # Aqui você colocaria seu algoritmo real (DFS, Prim, etc.)
        # Para o exemplo, vamos apenas embaralhar as linhas:
        random.shuffle(self.amaze)
        print("Novo labirinto!")


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
    app = VizuAmaze(exemplo_matriz, config_path='config.txt')
    app.run()