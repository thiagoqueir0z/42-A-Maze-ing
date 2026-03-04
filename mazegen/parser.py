import sys


def parse_config(file_path: str) -> dict:
    """
    Read and parse the configuration file.

    Args:
        file_path (str): Path to the .txt configuration file.

    Returns:
        dict: A dictionary containing the raw key-value pairs from the file.
    """
    config_data = {}

    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    config_data[key.strip()] = value.strip()

    except FileNotFoundError:
        sys.stderr.write(f"Error: The file '{file_path}' was not found.\n")
        sys.exit(1)

    return config_data


def validate_config(raw_data: dict) -> dict:
    """
   Convert raw string data from the config file into appropriate Python types.

    Args:
        raw_data (dict): Dictionary with string keys and values.

    Returns:
        dict: Validated dictionary with int, bool, and tuples.
    """
    valid_config = {}

    try:
        valid_config['WIDTH'] = int(raw_data['WIDTH'])
        valid_config['HEIGHT'] = int(raw_data['HEIGHT'])
        valid_config['SEED'] = int(raw_data.get('SEED', 0))

        valid_config['PERFECT'] = raw_data['PERFECT'].lower() == 'true'

        entry_coords = raw_data['ENTRY'].split(',')
        valid_config['ENTRY'] = (int(entry_coords[0]), int(entry_coords[1]))

        exit_coords = raw_data['EXIT'].split(',')
        valid_config['EXIT'] = (int(exit_coords[0]), int(exit_coords[1]))

        valid_config['OUTPUT_FILE'] = raw_data['OUTPUT_FILE']

    except KeyError as e:
        sys.stderr.write(f"Error: Missing Mandatory configuration key: {e}\n")
        sys.exit(1)
    except ValueError as e:
        sys.stderr.write(f"Error: Invalid value format in config file: {e}\n")
        sys.exit(1)

    return valid_config
