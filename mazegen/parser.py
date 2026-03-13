import re
import sys
from typing import Any


_FIELD_PATTERNS: dict[str, re.Pattern[str]] = {
    # Strictly a single integer (no spaces, no extra tokens)
    'WIDTH':       re.compile(r'^\d+$'),
    'HEIGHT':      re.compile(r'^\d+$'),
    'SEED':        re.compile(r'^\d+$'),
    'TILE_SIZE':   re.compile(r'^\d+$'),
    # Exactly two integers separated by a single comma, no spaces
    'ENTRY':       re.compile(r'^\d+,\d+$'),
    'EXIT':        re.compile(r'^\d+,\d+$'),
    # Case-insensitive true/false only
    'PERFECT':     re.compile(r'^(true|false)$', re.IGNORECASE),
    # Non-empty string with no whitespace (a valid filename)
    'OUTPUT_FILE': re.compile(r'^\S+$'),
}

_MANDATORY_KEYS: tuple[str, ...] = (
    'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT',
)


def parse_config(file_path: str) -> dict[str, Any]:
    """
    Read and parse the configuration file, validating each field's format.

    Args:
        file_path (str): Path to the .txt configuration file.

    Returns:
        dict[str, Any]: A dictionary with raw key-value pairs from the file.
    """
    config_data: dict[str, Any] = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Every non-comment line must follow the KEY=VALUE pattern
                if '=' not in line:
                    sys.stderr.write(
                        f"Error: Line {line_number} has no '=' separator: "
                        f"'{line}'\n"
                    )
                    sys.exit(1)

                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Reject lines where the key itself
                # contains spaces/extra tokens
                if ' ' in key or not key:
                    sys.stderr.write(
                        f"Error: Line {line_number} has an invalid key "
                        f"format: '{key}'\n"
                    )
                    sys.exit(1)

                # If we know this key, validate its value against the pattern
                if key in _FIELD_PATTERNS:
                    if not _FIELD_PATTERNS[key].match(value):
                        sys.stderr.write(
                            f"Error: Invalid value for '{key}' on line "
                            f"{line_number}: '{value}'\n"
                            f"  Expected format: "
                            f"{_FIELD_PATTERNS[key].pattern}\n"
                        )
                        sys.exit(1)

                config_data[key] = value

    except FileNotFoundError:
        sys.stderr.write(f"Error: The file '{file_path}' was not found.\n")
        sys.exit(1)

    # Check that all mandatory keys are present
    for key in _MANDATORY_KEYS:
        if key not in config_data:
            sys.stderr.write(
                f"Error: Mandatory key '{key}' is missing from the config.\n"
            )
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
        valid_config['WIDTH'] = int(raw_data['WIDTH'])
        valid_config['HEIGHT'] = int(raw_data['HEIGHT'])

        if valid_config['WIDTH'] <= 0 or valid_config['HEIGHT'] <= 0:
            raise ValueError("WIDTH and HEIGHT must be greater than zero.")

        valid_config['SEED'] = (
            int(raw_data['SEED']) if 'SEED' in raw_data else None
        )

        valid_config['PERFECT'] = (
            raw_data['PERFECT'].strip().lower() == 'true'
        )

        def parse_coords(s: str) -> tuple[int, int]:
            """Parse a ``'x,y'`` string into an integer tuple.

            Args:
                s (str): Coordinate string in ``'x,y'`` format.

            Returns:
                tuple[int, int]: The parsed (x, y) coordinate pair.
            """
            x_str, y_str = s.split(',')
            return (int(x_str.strip()), int(y_str.strip()))

        valid_config['ENTRY'] = parse_coords(raw_data['ENTRY'])
        valid_config['EXIT'] = parse_coords(raw_data['EXIT'])

        valid_config['OUTPUT_FILE'] = raw_data['OUTPUT_FILE'].strip()
        if not valid_config['OUTPUT_FILE']:
            raise ValueError("OUTPUT_FILE cannot be empty.")

        if 'TILE_SIZE' in raw_data:
            valid_config['TILE_SIZE'] = int(raw_data['TILE_SIZE'])
            if valid_config['TILE_SIZE'] <= 0:
                raise ValueError("TILE_SIZE must be greater than zero.")
        else:
            valid_config['TILE_SIZE'] = 16

        # Bounds checks
        ex_ent, ey_ent = valid_config['ENTRY']
        if not (
            0 <= ex_ent < valid_config['WIDTH']
            and 0 <= ey_ent < valid_config['HEIGHT']
        ):
            raise ValueError(
                f"ENTRY {valid_config['ENTRY']} is out of grid bounds."
            )

        ex_out, ey_out = valid_config['EXIT']
        if not (
            0 <= ex_out < valid_config['WIDTH']
            and 0 <= ey_out < valid_config['HEIGHT']
        ):
            raise ValueError(
                f"EXIT {valid_config['EXIT']} is out of grid bounds."
            )

        if valid_config['ENTRY'] == valid_config['EXIT']:
            raise ValueError("ENTRY and EXIT must be different coordinates.")

    except (KeyError, ValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    return valid_config
