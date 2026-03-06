import sys
import random
from typing import Optional


def save_maze_to_file(
        file_path: str, grid_hex: list[str], settings: dict, solution: str
) -> None:
    """
    Save the generated maze to a file in the required format.

    Args:
        file_path (str): Path to the output file.
        grid_hex (list): List of strings representing the maze rows in hex.
        settings (dict): The validated settings containing ENTRY and EXIT.
        solution (str): The path as a string of directions (N, S, E, W).
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for row in grid_hex:
                file.write(f"{row}\n")
            file.write("\n")
            entry_x, entry_y = settings['ENTRY']
            exit_x, exit_y = settings['EXIT']
            file.write(f"{entry_x}, {entry_y} {exit_x}, {exit_y}\n")
            file.write(f"{solution}\n")

    except IOError as e:
        sys.stderr.write(
            f"Error: Could not write to file '{file.path}': {e}\n"
        )
        sys.exit(1)


class MazeGenerator:
    """
    A class to generate random mazes with a unique solution.

    Attributes:
        width (int): Number of columns.
        height (int): Number of rows.
        seed (Optional[int]): Seed for random number generation.
        grid (list[list[int]]): 2D list representing the maze cells.
    """

    def __init__(self, width: int, height: int, seed: Optional[int] = None):
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

        if seed is not None:
            random.seed(seed)

        self.grid = [
            [0xF for _ in range(width)]
            for _ in range(height)
        ]

    def generate(self, perfect: bool = True) -> None:
        """
        Main method to trigger the maze generation algorithm.

        Args:
            perfect (bool): If True, generates a perfect maze.
        """
        pass

    def get_hex_grid(self) -> list[str]:
        """
        Convert the internal grid to the hexadecimal format.

        Returns:
            list[str]: A list of strings, each representing a row in hex.
        """
        hex_rows = []
        for row in self.grid:
            hex_row = "".join(f"{cell:X}" for cell in row)
            hex_rows.append(hex_row)
        return hex_rows
