from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
from time import perf_counter

from pyautogui import moveTo, click, pixelMatchesColor

import data
from image_detection import ImageDetection
import window_capture as wc


class Interfaces:

    def __handle_interface_action(decorated_method):
        """Decorator to handle interface actions."""
        @wraps(decorated_method)
        def wrapper(*args, **kwargs):
            decorated_method(*args, **kwargs)
            method_name_parts = decorated_method.__name__.split('_', 1)
            is_open_method = getattr(Interfaces, f"is_{method_name_parts[1]}_open")
            action = "clos" if method_name_parts[0] == "close" else "open"
            interface_name = method_name_parts[1].replace("_", " ").title()
            start_time = perf_counter()
            while perf_counter() - start_time <= 4:
                if (action == "open" and is_open_method()) or (action == "clos" and not is_open_method()):
                    log.info(f"Successfully {action}ed '{interface_name}' interface!")
                    return True
            log.error(f"Timed out while {action}ing '{interface_name}' interface!")
            return False
        return wrapper

    @staticmethod
    @__handle_interface_action
    def open_characteristics():
        log.info("Opening 'Characteristics' interface ... ")
        moveTo(613, 622)
        click()
    
    @staticmethod
    @__handle_interface_action
    def close_characteristics():
        log.info("Closing 'Characteristics' interface ... ")
        moveTo(613, 622)
        click()

    @staticmethod
    @__handle_interface_action
    def open_inventory():
        log.info("Opening 'Inventory' interface ... ")
        moveTo(690, 622)
        click()

    @staticmethod
    @__handle_interface_action
    def close_inventory():
        log.info("Closing 'Inventory' interface ... ")
        moveTo(690, 622)
        click()

    @staticmethod
    @__handle_interface_action
    def close_right_click_menu():
        log.info("Closing 'Right Click Menu' interface ... ")
        moveTo(929, 51)
        click(clicks=2)

    @staticmethod
    @__handle_interface_action
    def close_offer_or_invite():
        log.info("Ignoring player ... ")
        moveTo(466, 387) # Move to 'Ignore for the session' button
        click()

    @staticmethod
    @__handle_interface_action
    def close_information():
        log.info("Closing 'Information' interface ... ")
        moveTo(468, 377)
        click()

    @staticmethod
    def is_characteristics_open():
        return all((
            pixelMatchesColor(902, 117, (81, 74, 60)),
            pixelMatchesColor(870, 331, (81, 74, 60))
        ))

    @staticmethod
    def is_inventory_open():
        return all((
            pixelMatchesColor(276, 311, (150, 138, 111)),
            pixelMatchesColor(905, 116, (213, 207, 170)),
            pixelMatchesColor(327, 255, (81, 74, 60))
        ))

    @staticmethod
    def is_offer_or_invite_open():
        """Exchange, challenge offers & guild, group invites."""
        return all((
            pixelMatchesColor(406, 255, (81, 74, 60)),
            pixelMatchesColor(530, 255, (81, 74, 60)),
            pixelMatchesColor(284, 354, (213, 207, 170)),
            pixelMatchesColor(655, 354, (213, 207, 170)),
            pixelMatchesColor(427, 350, (255, 97, 0)),
            pixelMatchesColor(513, 350, (255, 97, 0))
        ))

    @staticmethod
    def is_information_open():
        """E.g. appears after a level up."""
        return all((
            pixelMatchesColor(463, 261, (81, 74, 60)),
            pixelMatchesColor(302, 377, (213, 207, 170)),
            pixelMatchesColor(503, 376, (255, 97, 0))
        ))
    
    @staticmethod
    def is_main_menu_open():
        return all((
            pixelMatchesColor(461, 230, (81, 74, 60)),
            pixelMatchesColor(540, 230, (81, 74, 60)),
            pixelMatchesColor(343, 257, (213, 207, 170)),
            pixelMatchesColor(589, 421, (213, 207, 170)),
            pixelMatchesColor(369, 278, (255, 97, 0))
        ))
    
    @staticmethod
    def is_caution_open():
        """E.g. the confirmation window when clicking logout on Main Menu."""
        return all((
            pixelMatchesColor(280, 297, (213, 207, 170)),
            pixelMatchesColor(654, 303, (213, 207, 170)),
            pixelMatchesColor(426, 369, (255, 97, 0)),
            pixelMatchesColor(518, 369, (255, 97, 0)),
            pixelMatchesColor(465, 269, (81, 74, 60))
        ))

    @staticmethod
    def is_login_screen_open():
        return len(
            ImageDetection.find_image(
                wc.WindowCapture.gamewindow_capture(),
                data.images.Interface.dofus_logo,
                confidence=0.995
            )
        ) > 0

    @staticmethod
    def is_right_click_menu_open():
        return len(
            ImageDetection.find_image(
                wc.WindowCapture.gamewindow_capture(),
                data.images.Interface.right_click_menu,
                confidence=0.995
            )
        ) > 0
