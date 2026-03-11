import math
import time
from typing import Any, Dict, Iterable, Tuple


class AnimatorMixin:
    """Manages path reveal animation and UI pulse effects."""

    def _build_path_animation_map(
        self,
        path_coords: Iterable[Tuple[int, int]],
    ) -> None:
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
        if not self.path_animation_enabled:
            return True
        reveal_pos = self.path_reveal_map.get((x, y))
        if reveal_pos is None:
            return True
        return reveal_pos < self.path_reveal_index

    def _reset_path_animation(self) -> None:
        self.path_reveal_index = 0
        self._last_animation_time = time.time()

    def _pulse_value(self, phase_shift: float = 0.0) -> float:
        return (math.sin(self.ui_phase + phase_shift) + 1.0) * 0.5

    def _animated_fortytwo_color(self) -> int:
        return self._scale_color(
            self.fortytwo_bg_color,
            0.75 + 0.35 * self._pulse_value(0.8),
        )

    def _loop_tick(self, _param: Any) -> None:
        now = time.time()
        should_render = False

        if (
            self.ui_animation_enabled
            and now - self._last_ui_animation_time
            >= self.ui_animation_interval
        ):
            self._last_ui_animation_time = now
            self.ui_phase += self.ui_phase_step
            should_render = True

        if (
            self.show_path
            and self.path_animation_enabled
            and self.path_reveal_index < self.path_reveal_max
        ):
            if now - self._last_animation_time >= self.path_animation_interval:
                self._last_animation_time = now
                self.path_reveal_index = min(
                    self.path_reveal_max,
                    self.path_reveal_index + self.path_animation_step,
                )
                should_render = True

        if should_render:
            self.render()
