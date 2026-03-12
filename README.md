# A-Maze-ing

*This project was developed as part of the 42 curriculum, aiming to explore maze generation algorithms, data structures, and graphical interfaces.*

## Description

**A-Maze-ing** is a robust system for the generation, export, and interactive visualization of mazes. It leverages the **Recursive Backtracker** algorithm to create complex, "perfect" mazes (mazes with no loops and exactly one path between any two points). The project features a dynamic graphical interface built with the **MiniLibX (MLX)** library, allowing users to explore and manipulate mazes in real-time.

### AI Integration
Artificial Intelligence was utilized as a strategic development partner throughout this project:
* **Documentation:** Assistant in generating standardized PEP 257 docstrings to ensure code maintainability.
* **Performance:** Refactoring of low-level pixel manipulation functions to optimize rendering speed.
* **Architecture:** Guided the implementation of a modular Mixin-based design for the visualizer.

---

## Technical Details

### Generation Algorithm: Recursive Backtracker
The core generation logic uses a **Depth-First Search (DFS)** approach. The algorithm moves randomly through the grid, "carving" paths by removing walls between cells. 



* **Backtracking:** When the algorithm hits a dead end, it uses a stack to backtrack to the last cell with unvisited neighbors.
* **Imperfect Mazes:** If `PERFECT=false` is set in the configuration, the system post-processes the maze to remove additional walls, creating cycles and multiple valid paths.

### Configuration File
The program is driven by a `.txt` configuration file using a `KEY=VALUE` format:
* `WIDTH`/`HEIGHT`: Grid dimensions (must be positive integers).
* `ENTRY`/`EXIT`: Coordinates defined as `x,y` (e.g., `0,0`).
* `PERFECT`: `true` for a perfect maze, `false` for cycles.
* `SEED`: (Optional) Integer to reproduce a specific maze.
* `TILE_SIZE`: Size of each maze cell in pixels for the UI.

---

## Architecture & File Structure

* **`a_maze_ing.py`**: The main entry point. It manages the application lifecycle: parsing configs, triggering generation, exporting the hexadecimal file, and launching the UI.
* **`visualizer.py`**: The engine of the graphical interface. It coordinates the MLX window and centralizes the logic from all rendering Mixins.
* **`generator.py`**: Contains the `MazeGenerator` class, responsible for the DFS carving logic and the BFS solution-finding algorithm.
* **`maze_data.py`**: A data processor that scales the bitwise grid into a 2N+1 character matrix for visual rendering.
* **`renderer.py`**: Provides low-level graphics functions, including direct pixel-buffer manipulation for fast drawing.
* **`tile_drawer.py`**: Logic for drawing specific maze tiles (walls, floors, and connective paths).
* **`animator.py`**: Manages visual effects like the path-reveal animation and the "pulsing" start/end markers.
* **`parser.py`**: Uses Regex to strictly validate configuration files.
* **`export.py`**: Handles the output of the maze and its solution to a standardized text file.

---

## Instructions

### Prerequisites
* Python 3.x
* **MiniLibX (MLX)** library installed and configured on your host system.

### Running the Project
To generate and visualize a maze, run:
```bash
python3 a_maze_ing.py config.txt

---

### Graphical Interface Controls

| Key | Action |
| :--- | :--- |
| **SPACE** | Regenerate a new maze with a new seed |
| **H** | Toggle the visibility of the solution path |
| **C** | Randomize the wall colors |
| **F** | Randomize the "42" pattern color |
| **ESC** | Safely close the application |

---

## Resources

* **MiniLibX:** Graphical library for X-Window.
* **Recursive Backtracking:** [Algorithm Overview](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Recursive_backtracker).
* **PEP 257:** [Docstring Conventions](https://peps.python.org/pep-0257/).

---

## Authors

* **mariaalm** (Maria Almeida)
* **thiferre** (Thiago Ferreira)