import sys
from typing import Any


def save_maze_to_file(
        file_path: str,
        grid_hex: list[str],
        settings: dict[str, Any],
        solution: str
) -> None:
    """
    Save the generated maze to a file in the required format.

    Args:
        file_path (str): Path to the output file.
        grid_hex (list): List of strings representing the maze rows in hex.
        settings (dict): The validated settings containing ENTRY and EXIT.
        solution (str): The path as a string of directions (N, S, E, W).
    """
    if not grid_hex:
        sys.stderr.write("Error: Cannot save empty maze grid.\n")
        sys.exit(1)

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for row in grid_hex:
                file.write(f"{row}\n")
            file.write("\n")
            entry_x, entry_y = settings['ENTRY']
            exit_x, exit_y = settings['EXIT']
            file.write(f"{entry_x},{entry_y}\n")
            file.write(f"{exit_x},{exit_y}\n")
            file.write(f"{solution}\n")

    except IOError as e:
        sys.stderr.write(
            f"Error: Could not write to file '{file_path}': {e}\n"
        )
        sys.exit(1)
