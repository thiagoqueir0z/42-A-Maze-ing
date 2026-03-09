import sys
from typing import Any


def parse_config(file_path: str) -> dict[str, Any]:
    """
    Read and parse the configuration file.

    Args:
        file_path (str): Path to the .txt configuration file.

    Returns:
        dict[str, Any]: A dictionary with raw key-value pairs from the file.
    """
    config_data: dict[str, Any] = {}

    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                # Ignore empty lines and comments (Chapter IV.3)
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    config_data[key.strip()] = value.strip()

    except FileNotFoundError:
        sys.stderr.write(f"Error: The file '{file_path}' was not found.\n")
        sys.exit(1)

    return config_data


def validate_config(raw_data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert raw string data from the config file into appropriate Python types.

    Args:
        raw_data (dict[str, Any]): Dictionary with string keys and values.

    Returns:
        dict[str, Any]: Validated dictionary with int, bool, and tuples.
    """
    valid_config: dict[str, Any] = {}

    try:
        # Mandatory integer validation
        valid_config['WIDTH'] = int(raw_data['WIDTH'])
        valid_config['HEIGHT'] = int(raw_data['HEIGHT'])
        # Optional SEED for reproducibility in Chapter IV.4
        if 'SEED' in raw_data:
            valid_config['SEED'] = int(raw_data['SEED'])
        else:
            valid_config['SEED'] = None

        # Boolean validation for PERFECT flag
        valid_config['PERFECT'] = raw_data['PERFECT'].strip().lower() == 'true'

        def parse_coords(s: str) -> tuple[int, int]:
            parts = [p.strip() for p in s.split(',')]
            if len(parts) != 2:
                raise ValueError(f"Invalid coordinate format: {s}")
            return (int(parts[0]), int(parts[1]))

        # Coordinate and filename validation
        valid_config['ENTRY'] = parse_coords(raw_data['ENTRY'])
        valid_config['EXIT'] = parse_coords(raw_data['EXIT'])
        valid_config['OUTPUT_FILE'] = raw_data['OUTPUT_FILE'].strip()

        # Logical constraints validation (Chapter IV.4)
        if valid_config['WIDTH'] <= 0 or valid_config['HEIGHT'] <= 0:
            raise ValueError("WIDTH and HEIGHT must be greater than zero.")
        # Entry bounds check
        ex_ent, ey_ent = valid_config['ENTRY']
        if not (
            0 <= ex_ent < valid_config['WIDTH'] and
            0 <= ey_ent < valid_config['HEIGHT']
        ):
            raise ValueError(
                f"ENTRY {valid_config['ENTRY']} is out of grid bounds."
            )
        # Exit bounds check
        ex_out, ey_out = valid_config['EXIT']
        if not (
            0 <= ex_out < valid_config['WIDTH'] and
            0 <= ey_out < valid_config['HEIGHT']
        ):
            raise ValueError(
                f"EXIT {valid_config['EXIT']} is out of grid bounds."
            )
        # Ensure entry and exit are different (Chapter IV.4)
        if valid_config['ENTRY'] == valid_config['EXIT']:
            raise ValueError("ENTRY and EXIT must be different coordinates.")

    except (KeyError, ValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    return valid_config
