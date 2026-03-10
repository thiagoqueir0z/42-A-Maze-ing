"""
Package for procedural maze generation and solving.
Provides tools for parsing configs, generating structures, and visual display.
"""
from .generator import MazeGenerator
from .parser import parse_config, validate_config
from .export import save_maze_to_file
from .maze_data import MazeData

_has_visualizer: bool
try:
    from .visualizer import MazeVisualizer
    _has_visualizer = True
except ImportError:
    _has_visualizer = False

__all__ = [
    'MazeGenerator',
    'parse_config',
    'validate_config',
    'save_maze_to_file',
    'MazeData',
    'MazeVisualizer',
    '_has_visualizer',
]
