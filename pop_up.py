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
        wait_time = 5

        while time.time() - start_time < wait_time:

            popup = self.__popups_detect()

            if popup:
                pyautogui.moveTo(x, y, duration=self.__move_duration)
                pyautogui.click()
            else:
                print("[INFO] Added player to ignore ... ")
                return True
        
        else:
            print(f"[INFO] Failed to add to ignore in {wait_time} seconds!")
            return False

    def __popups_detect(self):
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

    def __popups_close(self):
        """
        Close any pop-up/interface using 'ESC'.

        - Will try to detect 'Main Menu' pop-up that comes up when 'ESC'
        is pressed.
        - Keeps pressing 'ESC' until detected.
        - If detected within `timeout` seconds, presses 'ESC' one more
        time to close 'Main Menu'.
        - If not detected within 'timeout' seconds, exits out of
        program.

        Returns
        ----------
        True : bool
            If all pop-ups/interfaces were successfully closed.
        NoReturn
            Exits out of program if pop-ups couldn't be closed within
            `timeout` seconds.
        
        """
        dark_gray = (81, 74, 60)
        light_gray = (213, 207, 170)
        orange = (255, 97, 0)

        start_time = time.time()
        timeout = 10
        
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
                continue
            elif counter == len(pixels):
                pyautogui.press("esc")
                print("[INFO] Closed successfully!")
                return True

        else:
            print(f"[INFO] Failed to close pop-ups in {timeout} seconds!")
            return False

    def deal(self):
        """
        Deal with any pop-ups or interfaces.

        - If an offer is detected from another player, will add player
        to ignore. If for some reason failed to add to ignore, will try
        to close all pop-ups & interfaces.
        - If no offer is detected, will try to close all pop-ups & 
        interfaces.
        - If failed to close pop-ups & interfaces in `attempts_allowed`
        times, will exit program.

        Returns
        ----------
        True : bool
            If pop-ups interfaces were dealt with successfully.
        NoReturn
            Exit program if failed to deal with pop-ups & interfaces
            in `attempts_allowed` times.
        
        """
        attempts_total = 0
        attempts_allowed = 3
        offer_close_attempts = 0

        while attempts_total < attempts_allowed:

            offers_or_invites = self.__popups_detect()

            if offers_or_invites and offer_close_attempts < 3:
                print("[INFO] Offer from another player detected ... ")
                if self.__ignore_for_session():
                    return True
                else:
                    offer_close_attempts += 1
            else:
                print("[INFO] Closing every pop-up and interface ... ")
                if self.__popups_close():
                    return True
                else:
                    attempts_total += 1

        else:
            print(f"[ERROR] Failed to deal with pop-ups in {attempts_allowed} "
                  "attempts ... ")
            print("[ERROR] Exiting ... ")
            os._exit(1)
