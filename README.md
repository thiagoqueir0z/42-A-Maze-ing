*This project has been created as part of the 42 curriculum by mariaalm, thiferre.*

## Description

**A-Maze-ing** is a modular Python project for generating, exporting, and visualizing procedurally generated mazes driven by an external configuration file.

The project provides:

- A configurable **maze generator** using the **Recursive Backtracker (DFS)** algorithm.
- Support for **perfect mazes** (`PERFECT=true`), ensuring a single unique path between the entry and the exit.
- Optional **imperfect mazes** (`PERFECT=false`) by post-processing the grid to add cycles while preventing fully open 3×3 areas.
- A standardized **hexadecimal export format** (1 hex digit per cell).
- An interactive **MiniLibX (MLX)** visualizer with controls to regenerate, toggle solution visibility, and change colors.

---

## Instructions

### Requirements

- Python **3.10+**
- MiniLibX (MLX) is available in one of these ways:
  - Provided by the evaluator system; or
  - Bundled/available locally (depending on your repository setup)

### Install (quality tools)

```bash
make install
```

### Run

```bash
python3 a_maze_ing.py config.txt
```

Or:

```bash
make run
```

### Debug

```bash
make debug
```

### Lint / Type check

```bash
make lint
```

Strict mode:

```bash
make lint-strict
```

> Note: The `mazegen/mlx/` folder contains third-party MLX wrapper code and should be excluded from lint/type-checking rules if required by your local environment.

---

## Graphical Interface Controls

| Key | Action |
| :--- | :--- |
| **SPACE** | Regenerate a new maze |
| **H** | Toggle the visibility of the solution path |
| **C** | Randomize wall colors |
| **F** | Randomize the "42" pattern color |
| **ESC** | Close the application |

---

## Resources

### References

- **MiniLibX:** minimal X11 graphics library used in 42 projects.
- **Recursive Backtracker (DFS):** Maze generation algorithm overview (Wikipedia).
- **PEP 257:** Python docstring conventions.

### AI usage (mandatory disclosure)

AI was used as an assistant during development. The main uses were:

- **Documentation:** help drafting and standardizing docstrings and README wording.
- **Refactoring & code quality:** suggestions for reorganizing modules and improving readability while following flake8 constraints.
- **Debug support:** helping interpret linter/type-checker outputs and proposing fixes (e.g., mypy + mixins).

Tools used:
- **GitHub Copilot**
- **Claude**

All final technical decisions, validation, and integration were performed by the team.

---

## Configuration File Format

The program is driven by a `.txt` configuration file with one setting per line:

- Format: `KEY=VALUE`
- Comments: any line starting with `#` is ignored.
- Empty lines are ignored.

### Mandatory keys

- `WIDTH`: maze width (positive integer)
- `HEIGHT`: maze height (positive integer)
- `ENTRY`: entry coordinate as `x,y`
- `EXIT`: exit coordinate as `x,y`
- `OUTPUT_FILE`: output filename (no whitespace)
- `PERFECT`: `true` or `false`

### Optional keys

- `SEED`: integer seed for reproducible generation
- `TILE_SIZE`: integer size of each cell in pixels for the UI (default value may apply)

### Example

```txt
# Maze size
WIDTH=25
HEIGHT=25

# Entry / Exit
ENTRY=0,0
EXIT=24,8

# Output
OUTPUT_FILE=maze.txt

# Perfect maze (unique path)
PERFECT=true

# Reproducibility
SEED=42

# UI
TILE_SIZE=16
```

---

## Maze Generation Algorithm

### Chosen algorithm: Recursive Backtracker (DFS)

The maze is carved using a **Depth-First Search** strategy:

1. Start at the `ENTRY`.
2. Randomly choose an unvisited neighbor.
3. Remove the wall between the current cell and the chosen neighbor.
4. Continue until reaching a dead end, then backtrack.

This naturally produces a **spanning tree** of the grid, which guarantees that when `PERFECT=true`, there is **exactly one path** between any two reachable cells (including entry and exit).

### Why this algorithm was chosen (mandatory)

We selected the Recursive Backtracker because:

- It is simple to implement and reason about.
- It produces visually pleasing mazes with long corridors.
- It naturally guarantees the “perfect maze” property (unique path) without requiring extra steps.
- It runs fast enough for interactive regeneration in the MLX UI.

### Imperfect mode

When `PERFECT=false`, the generator post-processes the maze to remove additional internal walls with a small probability, creating cycles and multiple valid paths, while checking constraints to avoid fully open **3×3** areas.

---

## Output Format (Hex)

The exported maze file is written as:

1. The maze grid where each cell is a **single hexadecimal digit** representing the cell walls (bitwise).
2. A blank line.
3. The `ENTRY` coordinates: `x,y`
4. The `EXIT` coordinates: `x,y`
5. The solution path as a string using only: `N`, `E`, `S`, `W`

---

## Reusability (mandatory)

The project includes a reusable module named **`mazegen`**.

Reusable parts:

- `MazeGenerator`: generation + solution-finding (BFS)
- `parser`: strict parsing and validation of config files
- `export`: writing the hex grid + metadata output

These components can be reused without the MLX visualizer to integrate maze generation into other Python applications (e.g., games, procedural content tools).

### How to reuse

You can reuse the generator by importing the module and calling it from another script:

```python
from mazegen.generator import MazeGenerator

gen = MazeGenerator(width=25, height=25, seed=42)
gen.generate(entry=(0, 0), exit_p=(24, 8), perfect=True)

hex_grid = gen.get_hex_grid()
solution = gen.solution
```

If your repository provides a wheel, you may install it with pip (example):

```bash
pip install ./mazegen_mariaalm-1.0.0-py3-none-any.whl
```

---

## Team & Project Management (mandatory)

### Team members and roles

- **mariaalm** — Visual and graphical implementation (MiniLibX UI, rendering, colors, controls, and interactive visualization).
- **thiferre** — Backend implementation (configuration parsing/validation, maze generation, solution finding, and export format).

### Anticipated planning

We started by splitting the project into two main tracks (backend and visual/UI) so we could progress in parallel:

1. **Config & validation**  
   Define the config format and implement strict parsing/validation (KEY=VALUE, mandatory keys, bounds checks).

2. **Maze generation core**  
   Implement Recursive Backtracker (DFS) for `PERFECT=true`, add reproducibility via `SEED`, and encode the maze as a bitwise grid (N/E/S/W).

3. **Solving & export format**  
   Implement BFS solving to produce the `N/E/S/W` solution string and export the grid as the required hexadecimal format plus metadata.

4. **Visualization layer (MLX)**  
   Build the MLX window loop, rendering pipeline, and interactive controls (regen, show/hide path, color changes).

5. **Quality pass**  
   Ensure flake8 formatting, type hints, and docstrings across the codebase, and validate edge cases.

During implementation we iterated on the plan mainly due to constraint-driven changes:

- **Open-area constraints**: the requirement to avoid large open areas (e.g., “never a fully open 3×3”) led to changes in generation logic and additional validation, requiring some refactoring of the generator.
- **Architecture adjustments**: the visual layer evolved into a **mixin-based design** to keep responsibilities separated (animation, tile drawing, renderer primitives), which made the UI code cleaner and easier to maintain.
- **Tooling and strictness**: integrating lint/type-checking revealed a few adjustments needed for third-party MLX wrapper code (excluded from lint/type-checking) and for mixin attribute typing.

### What worked well

- **Clear separation between backend and UI**: the backend stayed reusable and testable, while the MLX visualizer remained modular through mixins.
- **Strict config parsing**: validating input early prevented subtle runtime errors and made debugging easier.
- **Reproducibility**: `SEED` support made it easy to reproduce mazes and troubleshoot generation/visual bugs.

### What could be improved

- **More automated tests**: adding unit tests for generation constraints (e.g., “no 3×3 open areas”) and export formatting would increase confidence and reduce regressions.
- **Stricter typing around mixins**: using `Protocol`/explicit attribute declarations consistently would reduce mypy friction and make intent clearer.
- **Better error recovery**: in edge cases where constraints prevent valid carving, adding a controlled retry strategy (instead of failing) would improve robustness.

### Tools used

- **GitHub** (version control and collaboration)
- **Notion** (notes and task tracking)
- **GitHub Copilot** and **Claude** (AI assistance as described above)

---

## Authors

- **mariaalm** (Maria Paula Almeida)
- **thiferre** (Thiago Ferreira)