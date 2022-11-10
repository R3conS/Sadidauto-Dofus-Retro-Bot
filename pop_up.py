"""Provides pop-up and interface closing functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import os
import time

import pyautogui

from window_capture import WindowCapture


class PopUp:
    """
    Holds methods related to dealing with pop-ups & interfaces.
    
    Methods
    ----------
    deal()
        Deal with any pop-ups or interfaces.
    interface()
        Open or close specified interface.
    
    """

    # Pyautogui mouse move duration. Default is 0.1 which is too fast.
    __move_duration = 0.15

    def __ignore_for_session(self):
        """Select 'Ignore for this session' during popup."""
        log.info("Ignoring player ... ")

        x, y = (466, 387)
        start_time = time.time()
        wait_time = 3

        while time.time() - start_time < wait_time:

            popup = self.__detect_offers()

            if popup:
                pyautogui.moveTo(x, y, duration=self.__move_duration)
                pyautogui.click()
            else:
                log.info("Added player to ignore!")
                return True
        
        else:
            log.error(f"Failed to add to ignore in {wait_time} seconds!")
            return False

    def __detect_offers(self):
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

    def __detect_interfaces(self):
        """Detect interfaces."""
        if self.__interface_information():
            return "info"
        elif self.__interface_main_menu():
            return "main_menu"
        elif self.__interface_banker_dialogue():
            return "other"
        elif self.__interface_characteristics():
            return "characteristics"
        elif self.__interface_spells():
            return "spells"
        elif self.__interface_inventory():
            return "inventory"
        elif self.__interface_quests():
            return "quests"
        elif self.__interface_map():
            return "map"
        elif self.__interface_friends():
            return "friends"
        elif self.__interface_guild():
            return "guild"
        elif self.__interface_mount():
            return "mount"
        else:
            return False

    def __interface_information(self):
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

    def __interface_main_menu(self):
        """Detect 'Main Menu' interface."""
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        px1 = pyautogui.pixelMatchesColor(461, 230, dark_gray)
        px2 = pyautogui.pixelMatchesColor(540, 230, dark_gray)
        px3 = pyautogui.pixelMatchesColor(343, 257, light_gray)
        if px1 and px2 and px3:
            return True 

    def __interface_banker_dialogue(self):
        """Detect Astrub banker dialogue interface."""
        white = (255, 255, 206)
        px1 = pyautogui.pixelMatchesColor(25, 255, white)
        px2 = pyautogui.pixelMatchesColor(123, 255, white)
        if px1 and px2:
            return True

    def __interface_characteristics(self):
        """Detect characteristics interface."""
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(902, 117, dark_gray)
        px2 = pyautogui.pixelMatchesColor(870, 331, dark_gray)
        if px1 and px2:
            return True

    def __interface_spells(self):
        """Detect spells interface."""
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(694, 108, dark_gray)
        px2 = pyautogui.pixelMatchesColor(728, 198, dark_gray)
        if px1 and px2:
            return True

    def __interface_inventory(self):
        """Detect inventory interface."""
        bland_brown = (150, 138, 111)
        bland_yellow = (213, 207, 170)
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(276, 311, bland_brown)
        px2 = pyautogui.pixelMatchesColor(905, 116, bland_yellow)
        px3 = pyautogui.pixelMatchesColor(327, 255, dark_gray)
        if px1 and px2 and px3:
            return True

    def __interface_quests(self):
        """Detect quests interface."""
        dark_gray = (81, 74, 60)
        lighter_gray = (147, 134, 108)
        px1 = pyautogui.pixelMatchesColor(731, 141, dark_gray)
        px2 = pyautogui.pixelMatchesColor(889, 542, lighter_gray)
        if px1 and px2:
            return True

    def __interface_map(self):
        """Detect map interface."""
        bland_yellow = (213, 207, 170)
        px1 = pyautogui.pixelMatchesColor(465, 68, bland_yellow)
        px2 = pyautogui.pixelMatchesColor(924, 309, bland_yellow)
        if px1 and px2:
            return True
    
    def __interface_friends(self):
        """Detect friends interface."""
        dark_gray = (81, 74, 60)
        bland_yellow = (190, 185, 152)
        px1 = pyautogui.pixelMatchesColor(583, 118, dark_gray)
        px2 = pyautogui.pixelMatchesColor(894, 572, bland_yellow)
        if px1 and px2:
            return True

    def __interface_guild(self):
        """Detect guild interface."""
        dark_gray = (81, 74, 60)
        bland_yellow = (213, 207, 170)
        px1 = pyautogui.pixelMatchesColor(745, 132, dark_gray)
        px2 = pyautogui.pixelMatchesColor(901, 590, bland_yellow)
        if px1 and px2:
            return True

    def __interface_mount(self):
        """Detect mount interface."""
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(865, 241, dark_gray)
        px2 = pyautogui.pixelMatchesColor(914, 365, dark_gray)
        if px1 and px2:
            return True

    def __close_popup_or_interface(self):
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
        wait_main_menu = 0.2
        # Colors
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        orange = (255, 97, 0)
        # Loop control variables.
        start_time = time.time()
        timeout = 5
        
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

    def __close_right_click_menu(self):
        """Close right mouse click menu."""
        pyautogui.moveTo(929, 51)
        pyautogui.click()

    def deal(self):
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
            self.__close_right_click_menu()
            # Detecting offers.
            offers = self.__detect_offers()

            if offers and ignore_attempts <= ignore_attempts_allowed:

                log.info("Offer from another player detected!")

                if self.__ignore_for_session():

                    interface = self.__detect_interfaces()

                    if interface == "info":
                        log.info("Information interface detected ... ")
                        log.info("Closing ... ")
                        pyautogui.moveTo(469, 376, duration=0.15)
                        pyautogui.click()
                        continue

                    if isinstance(interface, str) and interface != "info":
                        log.info("Interfaces detected ... ")
                        log.info("Closing ... ")
                        if self.__close_popup_or_interface():
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

                if self.__close_popup_or_interface():
                    return True
                else:
                    attempts_total += 1
                    continue

            elif not offers:

                interface = self.__detect_interfaces()

                if interface == "info":
                        log.info("Information interface detected ... ")
                        log.info("Closing ... ")
                        pyautogui.moveTo(469, 376, duration=0.15)
                        pyautogui.click()
                        continue

                if isinstance(interface, str) and interface != "info":
                    log.info("Interfaces detected ... ")
                    log.info("Closing ... ")
                    if self.__close_popup_or_interface():
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
            WindowCapture.on_exit_capture()

    def interface(self, interface, action):
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
                if self.__detect_interfaces() == interface:
                    log.info(f"Successfully opened {interface} interface!")
                    return True
            else:
                if not self.__detect_interfaces():
                    log.info(f"Successfully closed {interface} interface!")
                    return True
        else:
            if action == "open":
                log.error(f"Failed to open {interface} interface in {timeout}"
                          " seconds!")
            else:
                log.error(f"Failed to close {interface} interface in {timeout}"
                          " seconds!")  
            return False
