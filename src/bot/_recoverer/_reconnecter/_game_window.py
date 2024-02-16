from src.logger import get_logger

log = get_logger()

import pygetwindow as gw

from src.bot._exceptions import UnrecoverableException


def get_game_window(game_window_identifier: int | str):
    """Can be either a window handle (int) or a window title (str)."""
    if isinstance(game_window_identifier, int):
        return gw.Win32Window(game_window_identifier)
    elif isinstance(game_window_identifier, str):
        try:
            return gw.getWindowsWithTitle(game_window_identifier)[0]
        except IndexError:
            raise UnrecoverableException(f"Couldn't find window with title '{game_window_identifier}'!")
    else:
        raise UnrecoverableException("Invalid 'game_window_identifier' type!")


def resize_game_window(gw_window: gw.Win32Window, size: tuple[int, int]):
    log.info(f"Resizing game window to: {size}.")
    gw_window.resizeTo(*size)
    # Putting the window back to most top left corner. After resizing,
    # it is for some reason slightly moved off of the left side of the screen.
    gw_window.moveTo(-8, 0)
