"""Provides Dofus's game window manipulating functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import time

import pyautogui
import pygetwindow as gw

import pop_up as pu


class GameWindow:
    """
    Holds methods related to working with 'Dofus.exe' window.

    Methods
    ----------
    check_if_exists()
        Detect 'Dofus.exe' window.
    resize_and_move()
        Resize and move 'Dofus.exe' window.
    close()
        Close 'Dofus.exe' window.
    logout()
        Logout from 'Dofus'.

    """

    character_name = None
    official_version = None

    @classmethod
    def check_if_exists(cls):
        """
        Detect 'Dofus.exe' window.
        
        Returns
        ----------
        True : bool
            If window was detected succesfully.
        False : bool
            If window wasn't detected.

        """
        gmw = gw.getWindowsWithTitle(cls.character_name + " - Dofus Retro")
        if gmw:
            log.info("Game window successfully detected!")
            return True
        else:
            log.info("Couldn't find the game window. Please enter a valid"
                     "character name and make sure you are logged in.")
            return False

    @classmethod
    def resize_and_move(cls):
        """Resize and move 'Dofus.exe' window."""
        dfw = gw.getWindowsWithTitle(cls.character_name + " - Dofus Retro")[0]
        dfw.restore()
        dfw.activate()

        if not cls.official_version:
            # For Ascalion.
            dfw.resizeTo(950, 765) 
        elif cls.official_version:
            # For Official Dofus Retro.
            dfw.resizeTo(950, 785)

        dfw.moveTo(-8, 0)

    @classmethod
    def logout(cls):
        """Logout from 'Dofus'."""
        log.info("Logging out ... ")

        start_time = time.time()
        timeout = 15

        while time.time() - start_time < timeout:

            # Dealing with any open interfaces/offers.
            pu.PopUp.deal()

            # Opening 'Main Menu'.
            pyautogui.press("esc")
            time.sleep(0.5)

            if pu.PopUp.detect_interfaces() == "main_menu":

                pyautogui.moveTo(468, 318, duration=0.15)
                pyautogui.click()
                time.sleep(0.5)

                if pu.PopUp.detect_interfaces() == "caution":

                    pyautogui.moveTo(381, 371, duration=0.15)
                    pyautogui.click()
                    time.sleep(2.5)

                    if pu.PopUp.detect_interfaces() == "login_screen":
                        log.info("Logged out successfully!")
                        break

        else:
            log.error(f"Failed to log out!")
            cls.close()

    @staticmethod
    def close():
        """Close 'Dofus.exe' window."""
        log.info("Closing 'Dofus.exe' ... ")
        pyautogui.moveTo(910, 15, duration=0.15)
        pyautogui.click()
