import sys
import random
from typing import Optional, List, Tuple
from collections import deque


class MazeGenerator:
    """
    A class to generate random mazes with a unique solution.

    Attributes:
        width (int): Number of columns.
        height (int): Number of rows.
        seed (Optional[int]): Seed for random number generation.
        grid (list[list[int]]): 2D list representing the maze cells.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None
    ) -> None:
        """
        Initialize the generator with dimensions and an optional seed.

        Args:
            width (int): The width of the maze.
            height (int): The height of the maze.
            seed (Optional[int]): Random seed for reproducibility.
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.solution: str = ""
        self.pattern_42: set[Tuple[int, int]] = set()

        if seed is not None:
            random.seed(seed)

        self.grid: List[List[int]] = [
            [0xF for _ in range(width)]
            for _ in range(height)
        ]

    def _draw_42(self, visited: set[Tuple[int, int]]) -> None:
        """Draw the number 42 by blocking cells (mandatory requirement)."""
        self.pattern_42 = set()
        if self.width >= 9 and self.height >= 9:
            offset_x = self.width // 2 - 2
            offset_y = self.height // 2 - 2
            pattern: List[Tuple[int, int]] = [
                (0, 0), (0, 1), (0, 2),
                (1, 2),
                (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                (4, 0), (5, 0), (6, 0),
                (6, 1), (6, 2),
                (5, 2), (4, 2),
                (4, 3), (4, 4), (5, 4), (6, 4),
            ]

            for dx, dy in pattern:
                coords = (offset_x + dx, offset_y + dy)
                visited.add(coords)
                self.pattern_42.add(coords)
        else:
            sys.stderr.write(
                "Warning: Maze too small to render the '42' pattern.\n"
            )

    def _make_imperfect(self, chance: float = 0.05) -> None:
        """
        Remove random internal walls to create cycles
        while preventing 3x3 open areas.

        Args:
            chance (float): Probability of removing an internal wall.
        """
        def is_3x3_open(sx: int, sy: int) -> bool:
            """Helper to check if a 3x3 area starting is fully open."""
            if (
                sx < 0
                or sy < 0
                or sx + 2 >= self.width
                or sy + 2 >= self.height
            ):
                return False

            for y in range(sy, sy + 3):
                for x in range(sx, sx + 3):
                    if x < sx + 2 and (self.grid[y][x] & 2):
                        return False
                    if y < sy + 2 and (self.grid[y][x] & 4):
                        return False
            return True

        for y in range(self.height - 1):
            for x in range(self.width - 1):
                not_in_42 = (
                    (x, y) not in self.pattern_42
                    and (x + 1, y) not in self.pattern_42
                )
                if not_in_42:
                    if random.random() < chance and (self.grid[y][x] & 2):
                        self.grid[y][x] &= ~2
                        self.grid[y][x + 1] &= ~8

                        violates = any(
                            is_3x3_open(sx, sy)
                            for sx in range(x - 1, x + 1)
                            for sy in range(y - 2, y + 1)
                        )

                        if violates:
                            self.grid[y][x] |= 2
                            self.grid[y][x + 1] |= 8

                not_in_42_south = (
                    (x, y) not in self.pattern_42
                    and (x, y + 1) not in self.pattern_42
                )
                if not_in_42_south:
                    if random.random() < chance and (self.grid[y][x] & 4):
                        self.grid[y][x] &= ~4
                        self.grid[y + 1][x] &= ~1

                        violates = any(
                            is_3x3_open(sx, sy)
                            for sx in range(x - 2, x + 1)
                            for sy in range(y - 1, y + 1)
                        )

                        if violates:
                            self.grid[y][x] |= 4
                            self.grid[y + 1][x] |= 1

    def generate(
        self,
        entry: Tuple[int, int],
        exit_p: Tuple[int, int],
        perfect: bool = True
    ) -> None:
        """Carve the maze using Recursive Backtracker and find solution."""
        stack: List[Tuple[int, int]] = [entry]
        visited: set[Tuple[int, int]] = {entry}
        self._draw_42(visited)

        dirs: List[Tuple[int, int, int, int]] = [
            (0, -1, 1, 4),
            (1, 0, 2, 8),
            (0, 1, 4, 1),
            (-1, 0, 8, 2),
        ]

        while stack:
            cx, cy = stack[-1]

            neighbors: List[Tuple[int, int, int, int]] = []
            for dx, dy, bc, bn in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, bc, bn))

            if neighbors:
                nx, ny, bc, bn = random.choice(neighbors)
                self.grid[cy][cx] &= ~bc
                self.grid[ny][nx] &= ~bn
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not perfect:
            self._make_imperfect(chance=0.08)

        self.solution = self._solve_bfs(entry, exit_p)

    def _solve_bfs(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> str:
        """Find the shortest path using BFS to comply with requirements."""
        queue: deque[Tuple[Tuple[int, int], str]] = deque([(start, "")])
        visited: set[Tuple[int, int]] = {start}
        moves: List[Tuple[int, int, str, int]] = [
            (0, -1, "N", 1),
            (1, 0, "E", 2),
            (0, 1, "S", 4),
            (-1, 0, "W", 8),
        ]

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == end:
                return path

            for dx, dy, label, bit in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (
                        not (self.grid[cy][cx] & bit)
                        and (nx, ny) not in visited
                    ):
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + label))
        return ""

    def _get_path_string(self, path: List[Tuple[int, int]]) -> str:
        """Convert coordinate list to direction string (N, S, E, W)."""
        if not path:
            return ""
        dirs: List[str] = []
        for i in range(len(path) - 1):
            (x1, y1), (x2, y2) = path[i], path[i + 1]
            if y2 < y1:
                dirs.append("N")
            elif x2 > x1:
                dirs.append("E")
            elif y2 > y1:
                dirs.append("S")
            elif x2 < x1:
                dirs.append("W")

        return "".join(dirs)

    def get_hex_grid(self) -> List[str]:
        """
        Convert the internal grid to the hexadecimal format.

        Returns:
            List[str]: A list of strings, each representing a row in hex.
        """
        hex_rows: List[str] = []
        for row in self.grid:
            hex_row = "".join(f"{cell:X}" for cell in row)
            hex_rows.append(hex_row)
        return hex_rows
