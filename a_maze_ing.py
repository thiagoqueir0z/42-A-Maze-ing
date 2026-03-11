import sys
from mazegen.parser import parse_config, validate_config
from mazegen.generator import MazeGenerator
from mazegen.export import save_maze_to_file
from mazegen import _has_visualizer

if _has_visualizer:
    from mazegen.visualizer import MazeVisualizer


def main() -> None:
    """
    Main entry point for the maze generation program.
    Handles configuration, generation, output and visual display.
    """
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid number of arguments.\n")
        sys.stderr.write("Usage: python3 a_maze_ing.py <config_file>\n")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        # 1. Parse com tratamento de erros (Chapter IV.2 e IV.3)
        raw_settings = parse_config(config_path)
        settings = validate_config(raw_settings)

        # 2. Geração respeitando os requisitos mandatórios (Chapter IV.4)
        gen = MazeGenerator(
            settings['WIDTH'],
            settings['HEIGHT'],
            settings.get('SEED')
        )
        gen.generate(settings['ENTRY'], settings['EXIT'], settings['PERFECT'])

        # 3. Output Hexadecimal conforme Chapter IV.5
        output_filename = settings['OUTPUT_FILE']
        save_maze_to_file(
            output_filename,
            gen.get_hex_grid(),
            settings, gen.solution
        )
        print(f"Maze successfully saved to {output_filename}")

        # 4. Representação Visual do Chapter V
        if _has_visualizer:
            visualizer = MazeVisualizer(gen, settings)
            print("\n=== A-Maze-ing - Commands ===")
            print("  H       - Show/Hide path")
            print("  C       - Change wall color")
            print("  F       - Change 42 color")
            print("  SPACE   - Regen")
            print("  ESC     - Exit")
            visualizer.run()
        else:
            sys.stderr.write(
                "Warning: Visual display unavailable (mlx not installed).\n"
            )

    except FileNotFoundError:
        sys.stderr.write(
            f"Error: Configuration file '{config_path}' not found.\n"
        )
        sys.exit(1)
    except KeyError as e:
        sys.stderr.write(f"Error: Missing mandatory key in config: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
