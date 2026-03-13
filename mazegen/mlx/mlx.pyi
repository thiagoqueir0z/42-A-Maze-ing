from typing import Any, Callable, Optional


class Mlx:
    def __init__(self) -> None: ...

    def mlx_init(self) -> object: ...

    def mlx_new_window(
        self,
        mlx_ptr: object,
        width: int,
        height: int,
        title: str,
    ) -> object: ...

    def mlx_new_image(
        self,
        mlx_ptr: object,
        width: int,
        height: int,
    ) -> object: ...

    def mlx_get_data_addr(
        self,
        img_ptr: object,
    ) -> tuple[memoryview, int, int, int]: ...

    def mlx_put_image_to_window(
        self,
        mlx_ptr: object,
        win_ptr: object,
        img_ptr: object,
        x: int,
        y: int,
    ) -> int: ...

    def mlx_key_hook(
        self,
        win_ptr: object,
        callback: Optional[Callable[[int, Any], None]],
        param: Any,
    ) -> int: ...

    def mlx_hook(
        self,
        win_ptr: object,
        x_event: int,
        x_mask: int,
        callback: Optional[Callable[..., None]],
        param: Any,
    ) -> int: ...

    def mlx_loop_hook(
        self,
        mlx_ptr: object,
        callback: Optional[Callable[[Any], None]],
        param: Any,
    ) -> int: ...

    def mlx_loop(self, mlx_ptr: object) -> int: ...
