from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import moveTo, click, pixelMatchesColor

import data
import detection
import window_capture as wc


class Interfaces:

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

    def __with_timeout(interface: str, state: str, timeout_seconds: int = 3):
        """
        Decorator. Allows to check if the interface state is open/closed
        within the specified interval of time.
        """
        def is_action_successful(decorated_method):
            def decorated_method_wrapper():
                start_time = perf_counter()
                while perf_counter() - start_time <= timeout_seconds:
                    if decorated_method():
                        log.info(f"'{interface.title()}' interface is {state}.")
                        return True
                else:
                    log.error(f"Timed out while checking if '{interface.title()}' interface is {state}.")
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
    @__with_timeout("characteristics", "closed")
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
    @__with_timeout("inventory", "closed")
    def is_inventory_closed():
        return not all((
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
    @__with_timeout("offer/invite", "closed")
    def is_offer_or_invite_closed():
        return not all((
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
    @__with_timeout("information", "closed")
    def is_information_closed():
        return not all((
            pixelMatchesColor(463, 261, (81, 74, 60)),
            pixelMatchesColor(302, 377, (213, 207, 170)),
            pixelMatchesColor(503, 376, (255, 97, 0))
        ))

    @staticmethod
    @__with_timeout("main menu", "open")
    def is_main_menu_open():
        return all((
            pixelMatchesColor(461, 230, (81, 74, 60)),
            pixelMatchesColor(540, 230, (81, 74, 60)),
            pixelMatchesColor(343, 257, (213, 207, 170)),
            pixelMatchesColor(589, 421, (213, 207, 170)),
            pixelMatchesColor(369, 278, (255, 97, 0))
        ))
    
    @staticmethod
    @__with_timeout("main menu", "closed")
    def is_main_menu_closed():
        return not all((
            pixelMatchesColor(461, 230, (81, 74, 60)),
            pixelMatchesColor(540, 230, (81, 74, 60)),
            pixelMatchesColor(343, 257, (213, 207, 170)),
            pixelMatchesColor(589, 421, (213, 207, 170)),
            pixelMatchesColor(369, 278, (255, 97, 0))
        ))

    @staticmethod
    @__with_timeout("banker dialogue", "open")
    def is_banker_dialogue_open():
        """Astrub banker dialogue interface."""
        return all((
            pixelMatchesColor(25, 255, (255, 255, 206)),
            pixelMatchesColor(123, 255, (255, 255, 206))
        ))

    @staticmethod
    @__with_timeout("banker dialogue", "closed")
    def is_banker_dialogue_closed():
        return not all((
            pixelMatchesColor(25, 255, (255, 255, 206)),
            pixelMatchesColor(123, 255, (255, 255, 206))
        ))

    @staticmethod
    @__with_timeout("caution", "open")
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
    @__with_timeout("caution", "closed")
    def is_caution_closed():
        return not all((
            pixelMatchesColor(280, 297, (213, 207, 170)),
            pixelMatchesColor(654, 303, (213, 207, 170)),
            pixelMatchesColor(426, 369, (255, 97, 0)),
            pixelMatchesColor(518, 369, (255, 97, 0)),
            pixelMatchesColor(465, 269, (81, 74, 60))
        ))
      
    @staticmethod
    @__with_timeout("login screen", "open")
    def is_login_screen_open():
        return len(
            detection.Detection.find(
            wc.WindowCapture.gamewindow_capture(),
            data.images.Interface.dofus_logo,
            threshold=0.95
        )) > 0
