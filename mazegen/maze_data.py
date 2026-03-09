class MazeData:
    def __init__(self, generator, entry=None, exit_p=None):
        self.generator = generator
        self.entry = entry if entry is not None else (0, 0)
        self.exit_p = (
            exit_p if exit_p is not None
            else (generator.width - 1, generator.height - 1)
        )
        self.path = self._generate_path_list()
        self.matrix = self._generate_visual_matrix()

    def _generate_visual_matrix(self):
        viz_w = self.generator.width * 2 + 1
        viz_h = self.generator.height * 2 + 1
        matriz = [['W' for _ in range(viz_w)] for _ in range(viz_h)]
        
        for y in range(self.generator.height):
            for x in range(self.generator.width):
                vx, vy = x * 2 + 1, y * 2 + 1
                matriz[vy][vx] = '0'

                val = self.generator.grid[y][x]
                if not (val & 1):
                    matriz[vy - 1][vx] = '0'
                if not (val & 2):
                    matriz[vy][vx + 1] = '0'
                if not (val & 4):
                    matriz[vy + 1][vx] = '0'
                if not (val & 8):
                    matriz[vy][vx - 1] = '0'

        for px, py in self.path:
            if 0 <= py < viz_h and 0 <= px < viz_w and matriz[py][px] != 'W':
                matriz[py][px] = 'P'

        start_vx = self.entry[0] * 2 + 1
        start_vy = self.entry[1] * 2 + 1
        end_vx = self.exit_p[0] * 2 + 1
        end_vy = self.exit_p[1] * 2 + 1
        matriz[start_vy][start_vx] = 'S'
        matriz[end_vy][end_vx] = 'E'

        return matriz

    def _generate_path_list(self):
        solution = getattr(self.generator, 'solution', '')
        if not solution:
            return []

        curr_vx = self.entry[0] * 2 + 1
        curr_vy = self.entry[1] * 2 + 1
        coords = [(curr_vx, curr_vy)]

        moves = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}

        for move in solution:
            dx, dy = moves[move]
            for _ in range(2):
                curr_vx += dx
                curr_vy += dy
                coords.append((curr_vx, curr_vy))

        return coords