"""Provides pop-up and interface closing functionality."""

import os
import time

import pyautogui


class PopUp:
    """
    Holds methods related to dealing with pop-ups & interfaces.
    
    Methods
    ----------
    deal()
        Deal with any pop-ups or interfaces.
    
    """

    # Pyautogui mouse move duration. Default is 0.1 which is too fast.
    __move_duration = 0.15

    def __ignore_for_session(self):
        """Select 'Ignore for this session' during popup."""
        print("[INFO] Ignoring player ... ")

        x, y = (466, 387)
        start_time = time.time()
        wait_time = 3

        while time.time() - start_time < wait_time:

            popup = self.__detect_offers()

            if popup:
                pyautogui.moveTo(x, y, duration=self.__move_duration)
                pyautogui.click()
            else:
                print("[INFO] Added player to ignore!")
                return True
        
        else:
            print(f"[INFO] Failed to add to ignore in {wait_time} seconds!")
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
        """
        Detect interfaces.
        
        Note
        ----------
        `__interface_information()` has a different return value because
        the closing logic for this interface is different. Pressing
        'ESC' doesn't work.
        
        """
        if self.__interface_information():
            return "information"
        elif self.__interface_main_menu():
            return True
        elif self.__interface_banker_dialogue():
            return True
        elif self.__interface_characteristics():
            return True
        elif self.__interface_spells():
            return True
        elif self.__interface_inventory():
            return True
        elif self.__interface_quests():
            return True
        elif self.__interface_map():
            return True
        elif self.__interface_friends():
            return True
        elif self.__interface_guild():
            return True
        elif self.__interface_mount():
            return True
        else:
            return False

    def __interface_information(self):
        """
        Detect 'Information' interface.
        
        Usually appears after a level up.

        """
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(463, 261, dark_gray)
        px2 = pyautogui.pixelMatchesColor(577, 261, dark_gray)
        if px1 and px2:
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
        dark_gray = (81, 74, 60)
        px1 = pyautogui.pixelMatchesColor(424, 273, dark_gray)
        px2 = pyautogui.pixelMatchesColor(591, 279, dark_gray)
        if px1 and px2:
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
        px2 = pyautogui.pixelMatchesColor(880, 580, bland_yellow)
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
                print("[INFO] Closed successfully!")
                return True

        else:
            print(f"[INFO] Failed to close pop-ups/interfaces in {timeout} "
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

                print("[INFO] Offer from another player detected!")

                if self.__ignore_for_session():

                    interface = self.__detect_interfaces()

                    if interface == "information":
                        print("[INFO] Information interface detected ... ")
                        print("[INFO] Closing ... ")
                        pyautogui.moveTo(469, 376, duration=0.15)
                        pyautogui.click()
                        time.sleep(0.25)

                    if interface:
                        print("[INFO] Interfaces detected ... ")
                        print("[INFO] Closing interfaces ... ")
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

                print("[INFO] Declining offer with `ESC` ... ")

                if self.__close_popup_or_interface():
                    return True
                else:
                    attempts_total += 1
                    continue

            elif not offers:

                interface = self.__detect_interfaces()

                if interface == "information":
                        print("[INFO] Information interface detected ... ")
                        print("[INFO] Closing ... ")
                        pyautogui.moveTo(469, 376, duration=0.15)
                        pyautogui.click()
                        time.sleep(0.25)

                if interface:
                    print("[INFO] Interfaces detected ... ")
                    print("[INFO] Closing interfaces ... ")
                    if self.__close_popup_or_interface():
                        return True
                    else:
                        attempts_total += 1
                        continue
                else:
                    return True

        else:
            print("[ERROR] Failed to deal with pop-ups/interfaces in "
                  f"{attempts_allowed} attempts ... ")
            print("[ERROR] Exiting ... ")
            os._exit(1)
