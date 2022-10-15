"""Provides banking functionality."""

import time
import os
import random

import cv2 as cv
import pyautogui

from data import ImageData
from detection import Detection
from window_capture import WindowCapture


class Bank:
    """
    Holds methods related to banking.

    Public class attributes
    ----------
    img_list : list[str]
        `list` of banker 'NPC' images. Loaded in 'bot.py'.
    img_path : str
        Path to folder where images are stored. Loaded in 'bot.py'.
    
    Methods
    ----------
    get_pods_percentage()
        Get inventory pods percentage.
    inside_or_outside()
        Check if character is inside or outside Astrub bank.
    enter_bank()
        Move character inside of bank.
    exit_bank()
        Move character outside of bank.
    open_bank_vault()
        Open bank interface.
    close_bank_vault()
        Close bank interface.
    deposit_items()
        Deposit all items from inventory into bank.
    
    """

    # Private class attributes.
    # Pyautogui mouse movement duration. Default is '0.1', too fast.
    __move_duration = 0.15

    # Objects
    __detection = Detection()
    __window_capture = WindowCapture()

    # Public class attributes.
    # Stores banker 'NPC' image data. Loaded in 'bot.py'.
    img_list = None
    img_path = None

    def __inventory(self):
        """Get status of inventory (opened/closed)."""
        
        # Gray pixels inside inventory.
        px_1 = pyautogui.pixelMatchesColor(424, 273, (81, 74, 60))
        px_2 = pyautogui.pixelMatchesColor(591, 279, (81, 74, 60))
        px_3 = pyautogui.pixelMatchesColor(820, 116, (213, 207, 170))

        if px_1 and px_2 and px_3:
            return "opened"
        else:
            return "closed"

    def __open_inventory(self):
        """Open inventory."""
        print("[INFO] Opening inventory ... ")
        pyautogui.moveTo(x=692, y=620)
        pyautogui.click()
        time.sleep(1)

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if self.__inventory() == "opened":
                print("[INFO] Inventory opened!")
                return True
        else:
            print(f"[ERROR] Failed to open inventory in {wait_time} "
                  "seconds ... ")
            print(f"[ERROR] Timed out!")
            print(f"[ERROR] Exiting ... ")
            os._exit(1)

    def __close_inventory(self):
        """Close inventory."""
        print("[INFO] Closing inventory ... ")
        pyautogui.moveTo(x=692, y=620, duration=self.__move_duration)
        pyautogui.click()
        time.sleep(1)

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if self.__inventory() == "closed":
                print("[INFO] Inventory closed!")
                return True
        else:
            print(f"[ERROR] Failed to close inventory in {wait_time} "
                  "seconds ... ")
            print(f"[ERROR] Timed out!")
            print(f"[ERROR] Exiting ... ")
            os._exit(1)

    def __bank_vault(self):
        """Get status of bank vault (opened/closed)."""
        wait_time = 3
        start_time = time.time()

        while time.time() - start_time < wait_time:

            # Gray pixels inside bank vault interface.
            px_1 = pyautogui.pixelMatchesColor(218, 170, (81, 74, 60))
            px_2 = pyautogui.pixelMatchesColor(881, 172, (81, 74, 60))
            px_3 = pyautogui.pixelMatchesColor(700, 577, (213, 207, 170))

            if px_1 and px_2 and px_3:
                return "opened"

        else:
            return "closed"

    def __banker_detect_npc(self):
        """Detect banker NPC."""
        print("[INFO] Detecting banker ... ")

        start_time = time.time()
        wait_time = 10

        while time.time() - start_time < wait_time:

            screenshot = self.__window_capture.gamewindow_capture()
            rectangles, coordinates = self.__detection.detect_objects(
                    self.img_list,
                    self.img_path,
                    screenshot
                )

            if len(coordinates) > 0:
                print("[INFO] Banker detected!")
                return rectangles, coordinates
            
        else:
            print(f"[INFO] Failed to detect banker in '{wait_time}' seconds!")
            return False

    def __banker_open_dialogue(self, banker_coordinates):
        """
        Talk with banker.
        
        Parameters
        ----------
        banker_coordinates : Tuple[int, int]
            Coordinates (x, y) of banker.

        """
        print("[INFO] Talking with banker ... ")

        x, y = banker_coordinates
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click(button="right")

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            dialogue = pyautogui.pixelMatchesColor(333, 322, (255, 255, 206))

            if dialogue:
                print("[INFO] Successfully started dialogue!")
                return True
        
        else:
            print(f"[INFO] Failed to start dialogue in '{wait_time}' seconds!")
            return False

    def __banker_open_personal_safe(self):
        """Select first option during dialogue with banker."""
        print("[INFO] Selecting option 'Consult your personal safe' ... ")

        pyautogui.moveTo(294, 365, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            dialogue = pyautogui.pixelMatchesColor(333, 322, (255, 255, 206))

            if not dialogue:
                print("[INFO] Successfully selected!")
                return True
        
        else:
            print(f"[INFO] Failed to select option in '{wait_time}' seconds!")
            return False

    def __open_tab_equipment(self):
        """Open char's equipment tab when bank interface is open."""
        print("[INFO] Opening 'Equipment' tab ... ")

        pyautogui.moveTo(817, 205, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            gray_pixel = pyautogui.pixelMatchesColor(813, 199, (81, 74, 60))

            if gray_pixel:
                print("[INFO] Successfully opened!")
                return True
        
        else:
            print(f"[INFO] Failed to open tab in '{wait_time}' seconds!")
            return False

    def __open_tab_resources(self):
        """Open char's resources tab when bank interface is open."""
        print("[INFO] Opening 'Resources' tab ... ")

        pyautogui.moveTo(870, 205, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            gray_pixel = pyautogui.pixelMatchesColor(863, 199, (81, 74, 60))

            if gray_pixel:
                print("[INFO] Successfully opened!")
                return True
        
        else:
            print(f"[INFO] Failed to open tab in '{wait_time}' seconds!")
            return False

    def __deposit_item(self):
        """Move mouse to first inventory slot and double-click."""
        mouse_pos = pyautogui.position()
        slot = (710, 275)

        if mouse_pos != slot:
            pyautogui.moveTo(slot[0], slot[1], duration=self.__move_duration)

        pyautogui.keyDown("ctrl")
        pyautogui.click(clicks=2, interval=0.1)
        pyautogui.keyUp("ctrl")

    def __deposit_items(self):
        """Deposit items in opened tab."""
        print("[INFO] Depositing items ... ")

        start_time = time.time()
        wait_time = 300

        while time.time() - start_time < wait_time:

            if not self.__slot_empty():
                self.__deposit_item()
            else:
                print("[INFO] Successfully deposited!")
                return True

        else:
            print(f"[INFO] Failed to deposit items in '{wait_time}' seconds!")
            return False

    def __slot_empty(self):
        """Check if first inventory slot is empty."""
        empty_slot = cv.imread(ImageData.empty_bank_slot)
        slot_1_region = (684, 249, 53, 55)

        start_time = time.time()
        wait_time = 3 

        while time.time() - start_time < wait_time:

            slot_1 = self.__window_capture.custom_area_capture(slot_1_region)
            slot_1 = self.__detection.find(slot_1, empty_slot, threshold=0.9)

            if len(slot_1) <= 0:
                return False

        else:
            return True

    def __calculate_pods(self):
        """
        Calculate inventory pods percentage.

        It's not super precise, because calculation is based on how much
        the pods bar is filled with the orange color. It doesn't take
        the actual pod numbers into account at all. Inventory must be
        open, otherwise will almost always return 0.

        Returns
        ----------
        pods_percentage : int
            Character's pod percentage.

        """
        # 100% - (633, 338), 0% - (547, 338)
        pods_bar_full = (633, 338)
        pods_bar_empty = (547, 338)
        orange_color = (255, 102, 0)
        pods_percentage = 100
        x, y = pods_bar_full

        while True:

            orange_pixel = pyautogui.pixelMatchesColor(x, y, orange_color)

            if orange_pixel:
                return round(pods_percentage)
            elif x == pods_bar_empty[0]:
                return round(pods_percentage)
            else:
                x -= 1
                pods_percentage -= 1.1627
                continue

    def get_pods_percentage(self):
        """Get inventory pods percentage."""
        print("[INFO] Checking pod percentage ... ")

        if self.__inventory() == "closed":
            self.__open_inventory()

        pods_percentage = self.__calculate_pods()
        print(f"[INFO] Pods: ~ {pods_percentage} % ... ")

        if self.__inventory() == "opened":
            self.__close_inventory()

        return pods_percentage

    def inside_or_outside(self):
        """
        Check if character is inside or outside Astrub bank.
        
        Character must be on '4,-16' map.

        """
        color = (0, 0, 0)
        black_pixel_1 = pyautogui.pixelMatchesColor(117, 525, color)
        black_pixel_2 = pyautogui.pixelMatchesColor(821, 526, color)
        black_pixel_3 = pyautogui.pixelMatchesColor(454, 90, color)

        if black_pixel_1 and black_pixel_2 and black_pixel_3:
            return True
        else:
            return False

    def enter_bank(self):
        """Move character inside of bank."""
        print("[INFO] Entering bank ... ")

        x, y = (767, 205)
        pyautogui.keyDown('e')
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click()
        pyautogui.keyUp('e')

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if self.inside_or_outside():
                print("[INFO] Successfully entered!")
                return True
        else:
            print("[INFO] Failed to enter bank ... ")
            return False

    def exit_bank(self):
        """Move character outside of bank."""
        print("[INFO] Exiting bank ... ")

        x, y = (268, 494)
        pyautogui.keyDown('e')
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click()
        pyautogui.keyUp('e')

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if not self.inside_or_outside():
                print("[INFO] Successfully exited!")
                return True
        else:
            print("[INFO] Failed to exit bank ... ")
            return False

    def open_bank_vault(self):
        """Open bank interface."""
        print("[INFO] Opening bank vault ... ")

        attempts_total = 0
        attempts_allowed = 3

        while attempts_total < attempts_allowed:

            banker = self.__banker_detect_npc()

            if banker:
                _, coords = banker

                if self.__banker_open_dialogue(random.choice(coords)):
                    if self.__banker_open_personal_safe():
                        if self.__bank_vault() == "opened":
                            print("[INFO] Bank vault is open!")
                            return True

            else:
                attempts_total += 1

        else:
            print(f"[ERROR] Failed to open bank in '{attempts_total}' "
                  "attempts!")
            print(f"[ERROR] Exiting ... ")
            os._exit(1)

    def close_bank_vault(self):
        """Close bank interface."""
        print("[INFO] Closing bank vault ... ")

        x, y = (904, 173)
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            close_icon = pyautogui.pixelMatchesColor(x, y, (255, 255, 255))

            if not close_icon:
                print("[INFO] Successfully closed!")
                return True

        else:
            print(f"[INFO] Failed to close bank vault in '{wait_time}' "
                  "seconds!")
            return False

    def deposit_items(self):
        """
        Deposit all items from inventory into bank.
        
        Bank interface must be open.
        
        """
        tab_resources_empty = False
        tab_equipment_empty = False

        while True:

            if not tab_resources_empty:
                if self.__open_tab_resources():
                    if self.__deposit_items():
                        tab_resources_empty = True
                        continue

            elif not tab_equipment_empty:
                if self.__open_tab_equipment():
                    if self.__deposit_items():
                        tab_equipment_empty = True
                        continue

            elif tab_resources_empty and tab_equipment_empty:
                print("[INFO] No more items to deposit!")
                return True
