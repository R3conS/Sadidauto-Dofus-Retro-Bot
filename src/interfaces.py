from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import moveTo, click, pixelMatchesColor

import data
import detection
import window_capture as wc


class Interfaces:

    @classmethod
    def detect_interfaces(cls):
        """Detect any open interfaces."""
        if cls.is_characteristics_open():
            return "characteristics"
        elif cls.is_inventory_open():
            return "inventory"
        elif cls.is_open_offer_or_invite():
            return "offer"
        elif cls.is_open_information():
            return "info"
        elif cls.is_open_main_menu():
            return "main_menu"
        elif cls.is_open_banker_dialogue():
            return "other"
        elif cls.is_open_caution():
            return "caution"
        elif cls.is_open_login_screen():
            return "login_screen"
        return None

    @staticmethod
    def open_characteristics():
        log.info("Opening 'Characteristics' interface ... ")
        moveTo(613, 622)
        click()
    
    @staticmethod
    def close_characteristics():
        log.info("Closing 'Characteristics' interface ... ")
        moveTo(613, 622)
        click()

    @staticmethod
    def open_inventory():
        log.info("Opening 'Inventory' interface ... ")
        moveTo(690, 622)
        click()

    @staticmethod
    def close_inventory():
        log.info("Closing 'Inventory' interface ... ")
        moveTo(690, 622)
        click()

    @staticmethod
    def close_right_click_menu():
        moveTo(929, 51)
        click(clicks=2)

    def __with_timeout(interface_name: str, action: str, timeout_seconds: int = 3):
        """
        Decorator. Allows to check if the interface action is `True`
        within the specified interval of time.
        """
        def is_action_successful(decorated_method):
            def decorated_method_wrapper():
                nonlocal action
                action = "closed" if action == "close" else action
                start_time = perf_counter()
                while perf_counter() - start_time <= timeout_seconds:
                    if decorated_method():
                        log.info(f"'{interface_name.capitalize()}' interface is {action}.")
                        return True
                else:
                    log.error(f"Timed out while checking if '{interface_name.capitalize()}' interface is {action}.")
                    return False
            return decorated_method_wrapper
        return is_action_successful

    @staticmethod
    @__with_timeout("characteristics", "open")
    def is_characteristics_open():
        return all((
            pixelMatchesColor(902, 117, (81, 74, 60)),
            pixelMatchesColor(870, 331, (81, 74, 60))
        ))

    @staticmethod
    @__with_timeout("characteristics", "close")
    def is_characteristics_closed():
        return not all((
            pixelMatchesColor(902, 117, (81, 74, 60)),
            pixelMatchesColor(870, 331, (81, 74, 60))
        ))

    @staticmethod
    @__with_timeout("inventory", "open")
    def is_inventory_open():
        return all((
            pixelMatchesColor(276, 311, (150, 138, 111)),
            pixelMatchesColor(905, 116, (213, 207, 170)),
            pixelMatchesColor(327, 255, (81, 74, 60))
        ))

    @staticmethod
    @__with_timeout("inventory", "close")
    def is_inventory_closed():
        return not all((
            pixelMatchesColor(276, 311, (150, 138, 111)),
            pixelMatchesColor(905, 116, (213, 207, 170)),
            pixelMatchesColor(327, 255, (81, 74, 60))
        ))

    @staticmethod
    def is_open_offer_or_invite():
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
    def is_open_information():
        """E.g. appears after a level up."""
        return all((
            pixelMatchesColor(463, 261, (81, 74, 60)),
            pixelMatchesColor(302, 377, (213, 207, 170)),
            pixelMatchesColor(503, 376, (255, 97, 0))
        ))

    @staticmethod
    def is_open_main_menu():
        return all((
            pixelMatchesColor(461, 230, (81, 74, 60)),
            pixelMatchesColor(540, 230, (81, 74, 60)),
            pixelMatchesColor(343, 257, (213, 207, 170)),
            pixelMatchesColor(589, 421, (213, 207, 170)),
            pixelMatchesColor(369, 278, (255, 97, 0))
        ))

    @staticmethod
    def is_open_banker_dialogue():
        """Astrub banker dialogue interface."""
        return all((
            pixelMatchesColor(25, 255, (255, 255, 206)),
            pixelMatchesColor(123, 255, (255, 255, 206))
        ))

    @staticmethod
    def is_open_caution():
        """E.g. the confirmation window when clicking logout on Main Menu."""
        return all((
            pixelMatchesColor(280, 297, (213, 207, 170)),
            pixelMatchesColor(654, 303, (213, 207, 170)),
            pixelMatchesColor(426, 369, (255, 97, 0)),
            pixelMatchesColor(518, 369, (255, 97, 0)),
            pixelMatchesColor(465, 269, (81, 74, 60))
        ))
        
    @staticmethod
    def is_open_login_screen():
        return len(
            detection.Detection.find(
            wc.WindowCapture.gamewindow_capture(),
            data.images.Interface.dofus_logo,
            threshold=0.95
        )) > 0
