"""Provides banking functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.INFO, True)

import time
import os
import random

import cv2 as cv
import pyautogui

from data import ImageData
from detection import Detection
from pop_up import PopUp
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
    recall_potion()
        Check if 'Recall Potion' is available or not.
    use_recall_potion()
        Double click 'Recall Potion' in 'Items' bar.

    """

    # Private class attributes.
    # Pyautogui mouse movement duration. Default is '0.1', too fast.
    __move_duration = 0.15

    # Objects
    __detection = Detection()
    __window_capture = WindowCapture()
    __popup = PopUp()

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
        log.info("Opening inventory ... ")
        pyautogui.moveTo(x=692, y=620)
        pyautogui.click()
        # Giving time for inventory to open.
        time.sleep(0.25)

        start_time = time.time()
        wait_time = 3

        while time.time() - start_time < wait_time:
            if self.__inventory() == "opened":
                log.info("Inventory opened!")
                return True
        else:
            log.info(f"Failed to open inventory in {wait_time} "
                     "seconds ... ")
            return False

    def __close_inventory(self):
        """Close inventory."""
        log.info("Closing inventory ... ")
        pyautogui.moveTo(x=692, y=620, duration=self.__move_duration)
        pyautogui.click()
        # Giving time for inventory to close.
        time.sleep(0.25)

        start_time = time.time()
        wait_time = 3

        while time.time() - start_time < wait_time:
            if self.__inventory() == "closed":
                log.info("Inventory closed!")
                return True
        else:
            log.info(f"Failed to close inventory in {wait_time} "
                     "seconds ... ")
            return False

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
        log.info("Detecting banker ... ")

        start_time = time.time()
        wait_time = 7

        while time.time() - start_time < wait_time:

            screenshot = self.__window_capture.gamewindow_capture()
            rectangles, coordinates = self.__detection.detect_objects(
                    self.img_list,
                    self.img_path,
                    screenshot
                )

            if len(coordinates) > 0:
                log.info("Banker detected!")
                return rectangles, coordinates
            
        else:
            log.info(f"Failed to detect banker in {wait_time} seconds!")
            return False

    def __banker_open_dialogue(self, banker_coordinates):
        """
        Talk with banker.
        
        Parameters
        ----------
        banker_coordinates : Tuple[int, int]
            Coordinates (x, y) of banker.

        """
        log.info("Talking with banker ... ")

        x, y = banker_coordinates
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click(button="right")

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            dialogue = pyautogui.pixelMatchesColor(333, 322, (255, 255, 206))

            if dialogue:
                log.info("Successfully started dialogue!")
                return True
        
        else:
            log.info(f"Failed to start dialogue in {wait_time} seconds!")
            return False

    def __banker_open_personal_safe(self):
        """Select first option during dialogue with banker."""
        log.info("Selecting option 'Consult your personal safe' ... ")

        pyautogui.moveTo(294, 365, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            dialogue = pyautogui.pixelMatchesColor(333, 322, (255, 255, 206))

            if not dialogue:
                log.info("Successfully selected!")
                return True
        
        else:
            log.info(f"Failed to select option in {wait_time} seconds!")
            return False

    def __open_tab_equipment(self):
        """Open char's equipment tab when bank interface is open."""
        log.info("Opening 'Equipment' tab ... ")

        pyautogui.moveTo(817, 205, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            gray_pixel = pyautogui.pixelMatchesColor(813, 199, (81, 74, 60))

            if gray_pixel:
                log.info("Successfully opened!")
                return True
        
        else:
            log.info(f"Failed to open tab in '{wait_time}' seconds!")
            return False

    def __open_tab_resources(self):
        """Open char's resources tab when bank interface is open."""
        log.info("Opening 'Resources' tab ... ")

        pyautogui.moveTo(870, 205, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            gray_pixel = pyautogui.pixelMatchesColor(863, 199, (81, 74, 60))

            if gray_pixel:
                log.info("Successfully opened!")
                return True
        
        else:
            log.info(f"Failed to open tab in '{wait_time}' seconds!")
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
        log.info("Depositing items ... ")

        start_time = time.time()
        wait_time = 300

        while time.time() - start_time < wait_time:

            if not self.__slot_empty():
                self.__deposit_item()
            else:
                log.info("Successfully deposited!")
                return True

        else:
            log.info(f"Failed to deposit items in '{wait_time}' seconds!")
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
        the actual pod numbers into account at all. 
        
        Note
        ----------
        - Returns a false percentage if inventory is not open. 
        - Returns a false percentage if pop-up or interface is blocking 
        the pods bar.
        - Impossible to get anything between 1-13%. 
        - Minimum possible percentage if at least 1 pod is taken is 14%.
        - For 0% the inventory must be completely empty.

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
        log.info("Checking pod percentage ... ")
        start_time = time.time()
        timeout = 60

        while time.time() - start_time < timeout:

            # Checking for offers/interfaces and closing them.
            self.__popup.deal()

            if self.__inventory() == "closed":
                if not self.__open_inventory():
                    continue

            pods_percentage = self.__calculate_pods()
            log.info(f"Pods: ~ {pods_percentage} % ... ")

            # If pods percentage is 0, means a pop-up was blocking pods 
            # bar during calculation or inventory wasn't opened at all.
            # Have to recalculate, otherwise character will go kill mobs 
            # even if he's overloaded already.
            if pods_percentage <= 0:
                log.info("Recalculating pods percentage ... ")
                continue

            if self.__inventory() == "opened":
                if not self.__close_inventory():
                    continue

            return pods_percentage

        else:
            log.critical(f"Failed to get pods percentage in {timeout} "
                         "seconds ... ")
            log.critical("Timed out ... ")
            log.critical("Exiting ... ")
            os._exit(1)

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
        log.info("Entering bank ... ")

        x, y = (767, 205)
        pyautogui.keyDown('e')
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click()
        pyautogui.keyUp('e')

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if self.inside_or_outside():
                log.info("Successfully entered!")
                return True
        else:
            log.info("Failed to enter bank!")
            return False

    def exit_bank(self):
        """Move character outside of bank."""
        log.info("Exiting bank ... ")

        x, y = (268, 494)
        pyautogui.keyDown('e')
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click()
        pyautogui.keyUp('e')

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if not self.inside_or_outside():
                log.info("Successfully exited!")
                return True
        else:
            log.info("Failed to exit bank!")
            return False

    def open_bank_vault(self):
        """Open bank interface."""
        log.info("Opening bank vault ... ")

        banker = self.__banker_detect_npc()

        if banker:
            _, coords = banker
            if self.__banker_open_dialogue(random.choice(coords)):
                if self.__banker_open_personal_safe():
                    if self.__bank_vault() == "opened":
                        log.info("Bank vault is open!")
                        return True

        log.info("Failed to open bank vault!")
        return False

    def close_bank_vault(self):
        """Close bank interface."""
        log.info("Closing bank vault ... ")

        x, y = (904, 173)
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            close_icon = pyautogui.pixelMatchesColor(x, y, (255, 255, 255))

            if not close_icon:
                log.info("Successfully closed!")
                return True

        else:
            log.info(f"Failed to close bank vault in '{wait_time}' "
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
                log.info("No more items to deposit!")
                return True

    def recall_potion(self):
        """
        Check if 'Recall Potion' is available or not.
        
        Make sure the potion is in first slot of second 'Item' row.

        """
        color = (120, 151, 154)
        px = pyautogui.pixelMatchesColor(664, 725, color, tolerance=20)
        if px:
            log.info("'Recall Potion' is available!")
            return "available"
        else:
            log.info("'Recall Potion' is not available!")
            return "unavailable"

    def use_recall_potion(self):
        """
        Double click 'Recall Potion' in 'Items' bar.
        
        Make sure the potion is in first slot of second 'Items' row.

        """
        log.info("Using 'Recall Potion' ... ")
        x, y = (664, 725)
        pyautogui.moveTo(x, y, duration=self.__move_duration)
        pyautogui.click(clicks=2, interval=0.1)
        time.sleep(0.25)
