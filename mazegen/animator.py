import math
import time
from typing import Any, Dict, Iterable, Tuple


class Animator:
    """
    Manages path reveal animation and UI pulse effects.

    This component provides the timing logic and coordinate mapping necessary
    to animate the solution path cell-by-cell and create pulsing visual
    effects for special maze elements.
    """

    def _build_path_animation_map(
        self,
        path_coords: Iterable[Tuple[int, int]],
    ) -> None:
        """
        Map solution path coordinates to their sequence index for animation.

        Args:
            path_coords: An iterable of (x, y) coordinates representing
                the solution path in the visual matrix.
        """
        self.path_reveal_map: Dict[Tuple[int, int], int] = {}
        idx = 0
        for px, py in path_coords:
            if (
                0 <= py < self.rows
                and 0 <= px < self.cols
                and self.amaze[py][px] == 'P'
            ):
                if (px, py) not in self.path_reveal_map:
                    self.path_reveal_map[(px, py)] = idx
                    idx += 1
        self.path_reveal_max = idx
        self.path_reveal_index = 0
        self._last_animation_time = time.time()

    def _should_draw_path_cell(self, x: int, y: int) -> bool:
        """
        Determine if a path cell should be visible based on animation progress.

        Args:
            x: The horizontal grid coordinate.
            y: The vertical grid coordinate.

        Returns:
            True if the cell is within the revealed range or not part of the
            animated path, False otherwise.
        """
        if not self.path_animation_enabled:
            return True
        reveal_pos = self.path_reveal_map.get((x, y))
        if reveal_pos is None:
            return True
        return reveal_pos < self.path_reveal_index

    def _reset_path_animation(self) -> None:
        """Reset the path reveal sequence to the beginning."""
        self.path_reveal_index = 0
        self._last_animation_time = time.time()

    def _pulse_value(self, phase_shift: float = 0.0) -> float:
        """
        Calculate a sinusoidal value based on the current UI phase.

        Args:
            phase_shift: Offset added to the current phase for variation.

        Returns:
            A float between 0.0 and 1.0.
        """
        return (math.sin(self.ui_phase + phase_shift) + 1.0) * 0.5

    def _animated_fortytwo_color(self) -> int:
        """
        Calculate the current color for '42' patterns based on pulse phase.

        Returns:
            The hexadecimal color value scaled by the current pulse factor.
        """
        return self._scale_color(
            self.fortytwo_bg_color,
            0.75 + 0.35 * self._pulse_value(0.8),
        )

    def _loop_tick(self, _param: Any) -> None:
        """
        Handle per-frame animation updates and timing.

        Updates the UI pulse phase and increments the path reveal index if
        the specified intervals have passed. Triggers a redraw if any state
        changes.

        Args:
            _param: Unused parameter required by the MLX loop hook.
        """
        now = time.time()
        should_render = False

        # Handle UI pulse animation (e.g., wall glow or pattern colors)
        if (
            self.ui_animation_enabled
            and now - self._last_ui_animation_time
            >= self.ui_animation_interval
        ):
            self._last_ui_animation_time = now
            self.ui_phase += self.ui_phase_step
            should_render = True

        # Handle solution path step-by-step reveal
        if (
            self.show_path
            and self.path_animation_enabled
            and self.path_reveal_index < self.path_reveal_max
        ):
            if now - self._last_animation_time >= self.path_animation_interval:
                self._last_animation_time = now
                self.path_reveal_index += 1
                should_render = True

        if should_render:
            self.render()
