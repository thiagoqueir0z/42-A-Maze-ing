from typing import List, Optional, Set, Tuple

from .generator import MazeGenerator


Coord = Tuple[int, int]
Matrix = List[List[str]]


class MazeData:
    def __init__(
        self,
        generator: MazeGenerator,
        entry: Optional[Coord] = None,
        exit_p: Optional[Coord] = None,
    ) -> None:
        self.generator = generator
        self.entry: Coord = entry if entry is not None else (0, 0)
        self.exit_p: Coord = (
            exit_p if exit_p is not None
            else (generator.width - 1, generator.height - 1)
        )
        self.path: List[Coord] = self._generate_path_list()
        self.matrix: Matrix = self._generate_visual_matrix()

    def _generate_visual_matrix(self) -> Matrix:
        viz_w = self.generator.width * 2 + 1
        viz_h = self.generator.height * 2 + 1
        matriz: Matrix = [['W' for _ in range(viz_w)] for _ in range(viz_h)]
        pattern_42: Set[Coord] = getattr(self.generator, 'pattern_42', set())

        for y in range(self.generator.height):
            for x in range(self.generator.width):
                vx, vy = x * 2 + 1, y * 2 + 1
                if (x, y) in pattern_42:
                    matriz[vy][vx] = 'F'
                else:
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
            if (
                0 <= py < viz_h
                and 0 <= px < viz_w
                and matriz[py][px] != 'W'
                and matriz[py][px] != 'F'
            ):
                matriz[py][px] = 'P'

        start_vx = self.entry[0] * 2 + 1
        start_vy = self.entry[1] * 2 + 1
        end_vx = self.exit_p[0] * 2 + 1
        end_vy = self.exit_p[1] * 2 + 1
        if matriz[start_vy][start_vx] != 'F':
            matriz[start_vy][start_vx] = 'S'
        if matriz[end_vy][end_vx] != 'F':
            matriz[end_vy][end_vx] = 'E'

        return matriz

    def _generate_path_list(self) -> List[Coord]:
        solution = getattr(self.generator, 'solution', '')
        if not solution:
            return []

        curr_vx = self.entry[0] * 2 + 1
        curr_vy = self.entry[1] * 2 + 1
        coords: List[Coord] = [(curr_vx, curr_vy)]

        moves: dict[str, Coord] = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }

        for move in solution:
            dx, dy = moves[move]
            for _ in range(2):
                curr_vx += dx
                curr_vy += dy
                coords.append((curr_vx, curr_vy))

        return coords
