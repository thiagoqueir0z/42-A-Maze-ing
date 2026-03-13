import random


class Renderer:
    """
    Provide low-level pixel manipulation and color calculation methods.

    This component handles direct memory writing for rectangle drawing, tile
    rendering, and color transformations used by the visualizer.
    """

    def _fill_rect(
        self,
        x_px: int,
        y_px: int,
        width: int,
        height: int,
        color: int,
    ) -> None:
        """
        Fill a rectangular area in the image buffer with a specific color.

        Uses direct memory slicing for optimized row-by-row pixel filling,
        handling clipping against window boundaries
        and pixel-to-byte conversion.

        Args:
            x_px: The starting x-coordinate in pixels.
            y_px: The starting y-coordinate in pixels.
            width: The width of the rectangle in pixels.
            height: The height of the rectangle in pixels.
            color: Hexadecimal color value to apply.
        """
        if width <= 0 or height <= 0:
            return

        x0 = max(0, x_px)
        y0 = max(0, y_px)
        x1 = min(self.win_w, x_px + width)
        y1 = min(self.win_h, y_px + height)

        if x0 >= x1 or y0 >= y1:
            return

        bytes_per_pixel = max(1, self.bpp // 8)
        pixel = bytearray(bytes_per_pixel)
        pixel[0] = color & 0xFF
        if bytes_per_pixel >= 2:
            pixel[1] = (color >> 8) & 0xFF
        if bytes_per_pixel >= 3:
            pixel[2] = (color >> 16) & 0xFF
        if bytes_per_pixel >= 4:
            pixel[3] = 0xFF

        span_width = x1 - x0
        row_bytes = bytes(pixel) * span_width

        for py in range(y0, y1):
            row_start = (py * self.stride) + (x0 * bytes_per_pixel)
            row_end = row_start + len(row_bytes)
            self.img_data[row_start:row_end] = row_bytes

    def _draw_tile(self, cell_x: int, cell_y: int, color: int) -> None:
        """
        Draw a single grid cell as a colored square.

        Args:
            cell_x: The horizontal grid index.
            cell_y: The vertical grid index.
            color: Hexadecimal color value.
        """
        self._fill_rect(
            cell_x * self.tile_size,
            cell_y * self.tile_size,
            self.tile_size,
            self.tile_size,
            color,
        )

    def _scale_color(self, color: int, factor: float) -> int:
        """
        Adjust the brightness of a color by a given factor.

        Args:
            color: The base hexadecimal color.
            factor: Multiplication factor
            (e.g., 0.5 for darker, 1.5 for lighter).

        Returns:
            The resulting hexadecimal color clamped
            between 0x000000 and 0xFFFFFF.
        """
        def clamp(channel_value: int) -> int:
            return min(255, max(0, int(channel_value * factor)))

        return (
            (clamp((color >> 16) & 0xFF) << 16)
            | (clamp((color >> 8) & 0xFF) << 8)
            | clamp(color & 0xFF)
        )

    def _random_color(self) -> int:
        """
        Generate a random 24-bit hexadecimal color.

        Returns:
            An integer representing a color in 0xRRGGBB format.
        """
        return random.randint(0, 0xFFFFFF)
