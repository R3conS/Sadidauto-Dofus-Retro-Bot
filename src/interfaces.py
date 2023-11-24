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

    @staticmethod
    def check_state(interface: str, state: str):
        method_name = f"is_{interface}_open"
        interface = interface.replace("_", " ")
        if method_name in dir(Interfaces):
            method = getattr(Interfaces, method_name)
            start_time = perf_counter()
            while perf_counter() - start_time <= 4:
                if state == "open":
                    if method():
                        log.info(f"'{interface.title()}' interface is open.")
                        return True
                elif state == "closed":
                    if not method():
                        log.info(f"'{interface.title()}' interface is closed.")
                        return True
            else:
                log.error(f"Timed out while checking if '{interface.title()}' interface is open.")
                return False
        raise ValueError(f"Interface '{interface}' does not exist.")

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
    def is_banker_dialogue_open():
        """Astrub banker dialogue interface."""
        return all((
            pixelMatchesColor(25, 255, (255, 255, 206)),
            pixelMatchesColor(123, 255, (255, 255, 206))
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
            detection.Detection.find(
                wc.WindowCapture.gamewindow_capture(),
                data.images.Interface.dofus_logo,
                threshold=0.95
            )
        ) > 0

    @staticmethod
    def is_right_click_menu_open():
        return len(
            detection.Detection.find(
                wc.WindowCapture.gamewindow_capture(),
                data.images.Interface.right_click_menu,
                threshold=0.95
            )
        ) > 0
