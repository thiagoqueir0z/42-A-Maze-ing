import random
import sys
from collections import deque
from typing import List, Optional, Set, Tuple


class MazeGenerator:
    """
    Generate random mazes with optional cycles
    while preventing large open areas.

    The maze grid is stored as a bitwise matrix where each cell contains wall
    bits:
        - 1: North wall
        - 2: East wall
        - 4: South wall
        - 8: West wall

    Opening a wall means clearing the corresponding bit.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialize the generator with dimensions and an optional seed.

        Args:
            width (int): The width of the maze (columns).
            height (int): The height of the maze (rows).
            seed (Optional[int]): Random seed for reproducibility.
        """
        self.width = width
        self.height = height
        self.seed = seed

        self.solution: str = ""
        self.pattern_42: Set[Tuple[int, int]] = set()

        if seed is not None:
            random.seed(seed)

        self.grid: List[List[int]] = [
            [0xF for _ in range(width)]
            for _ in range(height)
        ]

    def _draw_42(self, visited: Set[Tuple[int, int]]) -> None:
        """
        Add the '42' pattern cells to the visited set before DFS carving.

        This prevents the DFS algorithm from carving through these cells.

        Args:
            visited (Set[Tuple[int, int]]): Visited set shared with the DFS.
        """
        self.pattern_42 = set()

        if self.width < 9 or self.height < 9:
            sys.stderr.write(
                "Warning: Maze too small to render the '42' pattern.\n"
            )
            return

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

    def _is_3x3_open(self, sx: int, sy: int) -> bool:
        """
        Check if a 3x3 block is fully open internally (no internal walls).

        Internal walls checked:
            - East walls within the 3 rows and first 2 columns.
            - South walls within the first 2 rows and 3 columns.

        Args:
            sx (int): Top-left x coordinate of the 3x3 block.
            sy (int): Top-left y coordinate of the 3x3 block.

        Returns:
            bool: True if the 3x3 block has no internal walls.
        """
        if sx < 0 or sy < 0:
            return False
        if sx + 2 >= self.width or sy + 2 >= self.height:
            return False

        for y in range(sy, sy + 3):
            for x in range(sx, sx + 2):
                if self.grid[y][x] & 2:
                    return False

        for y in range(sy, sy + 2):
            for x in range(sx, sx + 3):
                if self.grid[y][x] & 4:
                    return False

        return True

    def _creates_3x3_open_area(self, x: int, y: int) -> bool:
        """
        Check whether any nearby 3x3 block around (x, y) is fully open.

        Args:
            x (int): X coordinate near a modified wall.
            y (int): Y coordinate near a modified wall.

        Returns:
            bool: True if any nearby 3x3 open area exists.
        """
        for sy in range(y - 2, y + 1):
            for sx in range(x - 2, x + 1):
                if self._is_3x3_open(sx, sy):
                    return True
        return False

    def _try_open_wall(self, x: int, y: int, bit: int) -> bool:
        """
        Try to open a wall from cell (x, y) in the given direction.

        If opening creates a fully open 3x3 area, the change is reverted.

        Direction bits:
            - 1: North
            - 2: East
            - 4: South
            - 8: West

        Args:
            x (int): Current cell x.
            y (int): Current cell y.
            bit (int): Wall bit to remove in the current cell.

        Returns:
            bool: True if the wall was opened successfully, False otherwise.
        """
        mapping: dict[int, Tuple[int, int, int]] = {
            1: (0, -1, 4),
            2: (1, 0, 8),
            4: (0, 1, 1),
            8: (-1, 0, 2),
        }
        if bit not in mapping:
            return False

        dx, dy, opposite = mapping[bit]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False

        # Already open.
        if not (self.grid[y][x] & bit):
            return True

        # Open both sides.
        self.grid[y][x] &= ~bit
        self.grid[ny][nx] &= ~opposite

        # Validate 3x3 constraint around the affected cells.
        if (
            self._creates_3x3_open_area(x, y)
            or self._creates_3x3_open_area(nx, ny)
        ):
            self.grid[y][x] |= bit
            self.grid[ny][nx] |= opposite
            return False

        return True

    def _assert_no_3x3_open(self) -> None:
        """
        Assert that the final grid contains no fully open 3x3 areas.

        Raises:
            RuntimeError: If any forbidden 3x3 open area is detected.
        """
        for sy in range(self.height - 2):
            for sx in range(self.width - 2):
                if self._is_3x3_open(sx, sy):
                    raise RuntimeError(
                        f"Forbidden 3x3 open area at ({sx}, {sy})."
                    )

    def _make_imperfect(self, chance: float = 0.05) -> None:
        """
        Remove random internal walls to create cycles while blocking 3x3 opens.

        This method attempts to open additional walls with a given probability
        and uses `_try_open_wall` to validate and revert changes if they would
        create a fully open 3x3 area.

        Args:
            chance (float): Probability of opening a candidate internal wall.
        """
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                not_in_42_east = (
                    (x, y) not in self.pattern_42
                    and (x + 1, y) not in self.pattern_42
                )
                if not_in_42_east and random.random() < chance:
                    self._try_open_wall(x, y, 2)

                not_in_42_south = (
                    (x, y) not in self.pattern_42
                    and (x, y + 1) not in self.pattern_42
                )
                if not_in_42_south and random.random() < chance:
                    self._try_open_wall(x, y, 4)

    def generate(
        self,
        entry: Tuple[int, int],
        exit_p: Tuple[int, int],
        perfect: bool = True,
    ) -> None:
        """
        Carve the maze using Recursive Backtracker (DFS) with 3x3 blocking.

        The carving step uses `_try_open_wall` to guarantee that no 3x3 area
        becomes fully open in both perfect and imperfect modes.

        Args:
            entry (Tuple[int, int]): The starting cell (x, y).
            exit_p (Tuple[int, int]): The target cell (x, y).
            perfect (bool): If True, generates a perfect maze with a unique
                path. If False, removes additional walls to create cycles.
        """
        try:
            stack: List[Tuple[int, int]] = [entry]
            visited: Set[Tuple[int, int]] = {entry}
            self._draw_42(visited)

            dirs: List[Tuple[int, int, int]] = [
                (0, -1, 1),
                (1, 0, 2),
                (0, 1, 4),
                (-1, 0, 8),
            ]

            while stack:
                cx, cy = stack[-1]

                candidates: List[Tuple[int, int, int]] = []
                for dx, dy, bit in dirs:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in visited:
                            candidates.append((nx, ny, bit))

                if not candidates:
                    stack.pop()
                    continue

                random.shuffle(candidates)
                carved = False

                for nx, ny, bit in candidates:
                    if self._try_open_wall(cx, cy, bit):
                        visited.add((nx, ny))
                        stack.append((nx, ny))
                        carved = True
                        break

                if not carved:
                    stack.pop()

            if not perfect:
                self._make_imperfect(chance=0.08)

            self._assert_no_3x3_open()

            self.solution = self._solve_bfs(entry, exit_p)
            if not self.solution:
                sys.stderr.write(
                    "Error: No path found between ENTRY and EXIT.\n"
                )
                sys.exit(1)

        except Exception as e:
            sys.stderr.write(f"Error during maze generation: {e}\n")
            sys.exit(1)

    def _solve_bfs(self, start: Tuple[int, int], end: Tuple[int, int]) -> str:
        """
        Find the shortest path between two cells using BFS.

        Args:
            start (Tuple[int, int]): Starting cell (x, y).
            end (Tuple[int, int]): Target cell (x, y).

        Returns:
            str: A string of directions (N, E, S, W). Empty if no path exists.
        """
        queue: deque[Tuple[Tuple[int, int], str]] = deque([(start, "")])
        visited: Set[Tuple[int, int]] = {start}
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
                        (not (self.grid[cy][cx] & bit))
                        and ((nx, ny) not in visited)
                    ):
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + label))

        return ""

    def get_hex_grid(self) -> List[str]:
        """
        Convert the internal grid to the hexadecimal format.

        Returns:
            List[str]: List of strings, each representing a row in hex.
        """
        return ["".join(f"{cell:X}" for cell in row) for row in self.grid]
