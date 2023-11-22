"""Provides pop-up and interface closing functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import time

import pyautogui

import data
import detection
import window_capture as wc


class PopUp:
    """
    Holds methods related to dealing with pop-ups & interfaces.
    
    Methods
    ----------
    detect_interfaces()
        Detect any open interfaces.
    deal()
        Deal with any pop-ups or interfaces.
    interface()
        Open or close specified interface.
    close_right_click_menu()
        Close right mouse click menu.
    
    """

    @classmethod
    def detect_interfaces(cls):
        """Detect any open interfaces."""
        if cls.__interface_information():
            return "info"
        elif cls.__interface_main_menu():
            return "main_menu"
        elif cls.__interface_banker_dialogue():
            return "other"
        elif cls.__interface_caution():
            return "caution"
        elif cls.__interface_login_screen():
            return "login_screen"
        elif cls.__interface_characteristics():
            return "characteristics"
        elif cls.__interface_spells():
            return "spells"
        elif cls.__interface_inventory():
            return "inventory"
        elif cls.__interface_quests():
            return "quests"
        elif cls.__interface_map():
            return "map"
        elif cls.__interface_friends():
            return "friends"
        elif cls.__interface_guild():
            return "guild"
        elif cls.__interface_mount():
            return "mount"
        else:
            return False

    @classmethod
    def deal(cls):
        """
        Deal with any pop-ups or interfaces.

        Logic
        ----------
        - Close accidental mouse right click menu.
        - Detect offers.
            - If offer detected - try to add player to ignore.
                - If failed to add - increment `ignore_attempts`.
            - Elif offer detected and failed to add player to ignore
            `ignore_attempts_allowed` times - try to close everything 
            using `__close_popup_or_interface()`.
                - If closed - return `True`.
                - If failed to close - increment `attempts_total`.
            - Elif offer not detected.
                - Detect interfaces.
                    - If detected - try to close.
                        - If closed - return `True`.
                        - Else - increment `attempts_total`.
                    - If not detected - return `True`.

        Program will exit if: 
            - `attempts_total` < `attempts_allowed`.

        Returns
        ----------
        True : bool
            If pop-ups & interfaces were dealt with successfully.
        NoReturn
            Exit program if failed to deal with pop-ups & interfaces
            in `attempts_allowed` times.
        
        """
        attempts_total = 0
        attempts_allowed = 3
        ignore_attempts = 1
        ignore_attempts_allowed = 3

        while attempts_total < attempts_allowed:

            # Closing accidental mouse right-click menus.
            cls.close_right_click_menu()
            # Detecting offers.
            offers = cls.detect_offers()

            if offers and ignore_attempts <= ignore_attempts_allowed:

                log.info("Offer from another player detected!")

                if cls.__ignore_for_session():

                    interface = cls.detect_interfaces()

                    if interface == "info":
                        log.info("Information interface detected ... ")
                        log.info("Closing ... ")
                        pyautogui.moveTo(469, 376, duration=0.15)
                        pyautogui.click()
                        continue

                    if interface == "caution":
                        log.info("'Caution' interface detected ... ")
                        log.info("Closing ... ")
                        pyautogui.moveTo(557, 370, duration=0.15)
                        pyautogui.click()
                        continue

                    if (isinstance(interface, str) 
                        and interface != "info"
                        and interface != "caution"):
                        log.info("Interfaces detected ... ")
                        log.info("Closing ... ")
                        if cls.__close_popup_or_interface():
                            return True
                        else:
                            attempts_total += 1
                            continue
                    else:
                        return True

                else:
                    ignore_attempts += 1
                    continue

            elif offers and ignore_attempts >= ignore_attempts_allowed:

                log.info("Declining offer with `ESC` ... ")

                if cls.__close_popup_or_interface():
                    return True
                else:
                    attempts_total += 1
                    continue

            elif not offers:

                interface = cls.detect_interfaces()

                if interface == "info":
                        log.info("Information interface detected ... ")
                        log.info("Closing ... ")
                        pyautogui.moveTo(469, 376, duration=0.15)
                        pyautogui.click()
                        continue
                
                if interface == "caution":
                        log.info("'Caution' interface detected ... ")
                        log.info("Closing ... ")
                        pyautogui.moveTo(557, 370, duration=0.15)
                        pyautogui.click()
                        continue

                if (isinstance(interface, str) 
                    and interface != "info"
                    and interface != "caution"):
                    log.info("Interfaces detected ... ")
                    log.info("Closing ... ")
                    if cls.__close_popup_or_interface():
                        return True
                    else:
                        attempts_total += 1
                        continue
                else:
                    return True

        else:
            log.critical("Failed to deal with pop-ups/interfaces in "
                         f"{attempts_allowed} attempts!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @classmethod
    def interface(cls, interface, action):
        """
        Open or close specified interface.
        
        Parameters
        ----------
        interface : str
            Interface to perform `action` on.
        action : str
            Action to perform (open/close).
        
        Returns
        ----------
        True : bool
            If `action` performed successfully.
        False : bool
            If failed to perform `action`.
            
        """
        interfaces = {
                "characteristics": (613, 622),
                "spells": (651, 622),
                "inventory": (690, 622),
                "quests": (726, 622),
                "map": (763, 622),
                "friends": (800, 622),
                "guild": (837, 622),
                "mount": (874, 622),
                "alignment": (908, 622),
            }

        if interface not in interfaces.keys():
            log.error(f"Interface '{interface}' doesn't exist!")
            return False
        elif action not in ["open", "close"]:
            log.error(f"Action '{action}' is invalid!")
            return False

        if action == "open":
            log.info(f"Opening {interface} interface ... ")
        else:
            log.info(f"Closing {interface} interface ... ") 

        x, y = interfaces[interface]
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click()
        time.sleep(0.35)

        start_time = time.time()
        timeout = 5

        while time.time() - start_time < timeout:
            if action == "open":
                if cls.detect_interfaces() == interface:
                    log.info(f"Successfully opened '{interface}' interface!")
                    return True
            else:
                if not cls.detect_interfaces():
                    log.info(f"Successfully closed '{interface}' interface!")
                    return True
        else:
            if action == "open":
                log.error(f"Failed to open '{interface}' interface in "
                          f"{timeout} seconds!")
            else:
                log.error(f"Failed to close '{interface}' interface in "
                          f"{timeout} seconds!")
            return False

    @staticmethod
    def close_right_click_menu():
        """Close right mouse click menu."""
        pyautogui.moveTo(929, 51)
        pyautogui.click(clicks=2)

    @staticmethod
    def detect_offers():
        """Detect exchange, challenge offers & guild, group invites."""
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        orange = (255, 97, 0)

        px_1 = pyautogui.pixelMatchesColor(406, 255, dark_gray)
        px_2 = pyautogui.pixelMatchesColor(530, 255, dark_gray)
        px_3 = pyautogui.pixelMatchesColor(284, 354, light_gray)
        px_4 = pyautogui.pixelMatchesColor(655, 354, light_gray)
        px_5 = pyautogui.pixelMatchesColor(427, 350, orange)
        px_6 = pyautogui.pixelMatchesColor(513, 350, orange)

        pixels = [px_1, px_2, px_3, px_4, px_5, px_6]

        counter = 0
        for pixel in pixels:
            if pixel: 
                counter += 1

        if counter == len(pixels):
            return True
        else:
            return False

    @classmethod
    def __ignore_for_session(cls):
        """Select 'Ignore for this session' during popup."""
        log.info("Ignoring player ... ")

        x, y = (466, 387)
        start_time = time.time()
        wait_time = 3

        while time.time() - start_time < wait_time:

            popup = cls.detect_offers()

            if popup:
                pyautogui.moveTo(x, y, duration=0.15)
                pyautogui.click()
            else:
                log.info("Added player to ignore!")
                return True
        
        else:
            log.error(f"Failed to add to ignore in {wait_time} seconds!")
            return False

    @staticmethod
    def __interface_information():
        """
        Detect 'Information' interface.
        
        Usually appears after a level up.

        """
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        orange = (255, 97, 0)
        px1 = pyautogui.pixelMatchesColor(463, 261, dark_gray)
        px2 = pyautogui.pixelMatchesColor(302, 377, light_gray)
        px3 = pyautogui.pixelMatchesColor(503, 376, orange)
        if px1 and px2 and px3:
            return True

    @staticmethod
    def __interface_main_menu():
        """Detect 'Main Menu' interface."""
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        px1 = pyautogui.pixelMatchesColor(461, 230, dark_gray)
        px2 = pyautogui.pixelMatchesColor(540, 230, dark_gray)
        px3 = pyautogui.pixelMatchesColor(343, 257, light_gray)
        if px1 and px2 and px3:
            return True 

    @staticmethod
    def __interface_banker_dialogue():
        """Detect Astrub banker dialogue interface."""
        white = (255, 255, 206)
        px1 = pyautogui.pixelMatchesColor(25, 255, white)
        px2 = pyautogui.pixelMatchesColor(123, 255, white)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_caution():
        light_gray = (213, 207, 170)
        orange = (255, 97, 0)
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(280, 297, light_gray)
        px2 = pyautogui.pixelMatchesColor(654, 303, light_gray)
        px3 = pyautogui.pixelMatchesColor(426, 369, orange)
        px4 = pyautogui.pixelMatchesColor(518, 369, orange)
        px5 = pyautogui.pixelMatchesColor(465, 269, dark_gray)
        if px1 and px2 and px3 and px4 and px5:
            return True

    @staticmethod
    def __interface_login_screen():
        sc = wc.WindowCapture.gamewindow_capture()
        rects = detection.Detection.find(sc,
                                         data.images.Interface.dofus_logo,
                                         threshold=0.95)
        if len(rects) > 0:
            return True

    @staticmethod
    def __interface_characteristics():
        """Detect characteristics interface."""
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(902, 117, dark_gray)
        px2 = pyautogui.pixelMatchesColor(870, 331, dark_gray)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_spells():
        """Detect spells interface."""
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(694, 108, dark_gray)
        px2 = pyautogui.pixelMatchesColor(728, 198, dark_gray)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_inventory():
        """Detect inventory interface."""
        bland_brown = (150, 138, 111)
        bland_yellow = (213, 207, 170)
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(276, 311, bland_brown)
        px2 = pyautogui.pixelMatchesColor(905, 116, bland_yellow)
        px3 = pyautogui.pixelMatchesColor(327, 255, dark_gray)
        if px1 and px2 and px3:
            return True

    @staticmethod
    def __interface_quests():
        """Detect quests interface."""
        dark_gray = (81, 74, 60)
        lighter_gray = (147, 134, 108)
        px1 = pyautogui.pixelMatchesColor(731, 141, dark_gray)
        px2 = pyautogui.pixelMatchesColor(889, 542, lighter_gray)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_map():
        """Detect map interface."""
        bland_yellow = (213, 207, 170)
        px1 = pyautogui.pixelMatchesColor(465, 68, bland_yellow)
        px2 = pyautogui.pixelMatchesColor(924, 309, bland_yellow)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_friends():
        """Detect friends interface."""
        dark_gray = (81, 74, 60)
        bland_yellow = (190, 185, 152)
        px1 = pyautogui.pixelMatchesColor(583, 118, dark_gray)
        px2 = pyautogui.pixelMatchesColor(894, 572, bland_yellow)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_guild():
        """Detect guild interface."""
        dark_gray = (81, 74, 60)
        bland_yellow = (213, 207, 170)
        px1 = pyautogui.pixelMatchesColor(745, 132, dark_gray)
        px2 = pyautogui.pixelMatchesColor(901, 590, bland_yellow)
        if px1 and px2:
            return True

    @staticmethod
    def __interface_mount():
        """Detect mount interface."""
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(865, 241, dark_gray)
        px2 = pyautogui.pixelMatchesColor(914, 365, dark_gray)
        if px1 and px2:
            return True

    @staticmethod
    def __close_popup_or_interface():
        """
        Close any pop-up/interface using 'ESC'.
        
        Logic
        ----------
        - Keep pressing 'ESC' until 'Main Menu' interface is detected.
            - If detected within `timeout` seconds - press 'ESC' one
            more time to close 'Main Menu'.
            - If not detected within `timeout` seconds - exit out of
            program.

        Returns
        ----------
        True : bool
            If all pop-ups/interfaces were successfully closed.
        NoReturn
            Exits out of program if pop-ups couldn't be closed within
            `timeout` seconds.
        
        """
        # Waiting for 'Main Menu' interface to appear/disappear.
        wait_main_menu = 0.25
        # Colors
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        orange = (255, 97, 0)
        # Loop control variables.
        start_time = time.time()
        timeout = 7
        
        while time.time() - start_time < timeout:

            px_1 = pyautogui.pixelMatchesColor(461, 230, dark_gray)
            px_2 = pyautogui.pixelMatchesColor(540, 230, dark_gray)
            px_3 = pyautogui.pixelMatchesColor(343, 257, light_gray)
            px_4 = pyautogui.pixelMatchesColor(589, 421, light_gray)
            px_5 = pyautogui.pixelMatchesColor(369, 278, orange)
            px_6 = pyautogui.pixelMatchesColor(565, 401, orange)

            pixels = [px_1, px_2, px_3, px_4, px_5, px_6]

            counter = 0
            for pixel in pixels:
                if pixel: 
                    counter += 1

            if counter != len(pixels):
                pyautogui.press("esc")
                time.sleep(wait_main_menu)
                continue
            elif counter == len(pixels):
                pyautogui.press("esc")
                log.info("Closed successfully!")
                return True

        else:
            log.error(f"Failed to close pop-ups/interfaces in {timeout} "
                      "seconds!")
            return False
