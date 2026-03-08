import sys
from mazegen.parser import parse_config
from mazegen.generator import MazeGenerator, save_maze_to_file

def main() -> None:
    """
    Main entry point for the maze generation program.
    Reads configuration, generates the maze, and saves the output.
    """
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid number of arguments.\n")
        sys.stderr.write("Usage: python3 a_maze_ing.py <config_file>\n")
        sys.exit(1)

    config_path = sys.argv[7]

    # 1. Parse com tratamento de erros (conforme Chapter IV.2)
    settings = parse_config(config_path)

    # 2. Geração respeitando a Seed e a flag PERFECT (Chapter IV.3 e IV.4)
    gen = MazeGenerator(settings['WIDTH'], settings['HEIGHT'], settings['SEED'])
    gen.generate(settings['ENTRY'], settings['EXIT'], settings['PERFECT'])

    # 3. Output usando o nome definido no config (Chapter IV.5)
    output_filename = settings['OUTPUT_FILE']
    save_maze_to_file(output_filename, gen.get_hex_grid(), settings, gen.solution)
    
    print(f"Maze generated and saved to {output_filename}")

if __name__ == "__main__":
    main()
