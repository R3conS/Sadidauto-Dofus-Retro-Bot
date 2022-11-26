"""Provides banking functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import time
import random

import cv2 as cv
import pyautogui

import data
import detection as dtc
import pop_up as pu
import window_capture as wc


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
    enter_bank()
        Move character inside of bank.
    exit_bank()
        Move character outside of bank.
    deposit_items()
        Deposit all items from inventory into bank.
    open_bank_vault()
        Open bank interface.
    close_bank_vault()
        Close bank interface.
    inside_or_outside()
        Check if character is inside or outside Astrub bank.
    recall_potion()
        Check if 'Recall Potion' is available or not.
    use_recall_potion()
        Double click 'Recall Potion' in 'Items' bar.

    """

    # Public class attributes.
    # Stores banker 'NPC' image data. Loaded in 'bot.py'.
    img_list = None
    img_path = None
    # Stores whether on official Dofus servers or not.
    official_version = None

    @classmethod
    def get_pods_percentage(cls):
        """Get inventory pods percentage."""
        log.info("Checking pod percentage ... ")
        start_time = time.time()
        timeout = 60

        while time.time() - start_time < timeout:

            # Checking for offers/interfaces and closing them.
            pu.PopUp.deal()

            if cls.__inventory() == "closed":
                if not pu.PopUp.interface("inventory", "open"):
                    continue

            pods_percentage = cls.__calculate_pods()
            log.info(f"Pods: ~ {pods_percentage} % ... ")

            # If pods percentage is 0, means a pop-up was blocking pods 
            # bar during calculation or inventory wasn't opened at all.
            # Have to recalculate, otherwise character will go kill mobs 
            # even if he's overloaded already.
            if pods_percentage <= 0:
                log.info("Recalculating pods percentage ... ")
                continue

            if cls.__inventory() == "opened":
                if not pu.PopUp.interface("inventory", "close"):
                    continue

            return pods_percentage

        else:
            log.critical(f"Failed to get percentage in {timeout} seconds!")
            log.critical("Timed out!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @classmethod
    def enter_bank(cls):
        """Move character inside of bank."""
        log.info("Entering bank ... ")

        coords = [(767, 205), (792, 203), (765, 193), (761, 215), (748, 201)]
        x, y = random.choice(coords)

        pyautogui.keyDown('e')
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click()
        pyautogui.keyUp('e')

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if cls.inside_or_outside():
                log.info("Successfully entered!")
                return True
        else:
            log.error("Failed to enter bank!")
            return False

    @classmethod
    def exit_bank(cls):
        """Move character outside of bank."""
        log.info("Exiting bank ... ")

        x, y = (268, 494)
        pyautogui.keyDown('e')
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click()
        pyautogui.keyUp('e')

        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:
            if not cls.inside_or_outside():
                log.info("Successfully exited!")
                return True
        else:
            log.error("Failed to exit bank!")
            return False

    @classmethod
    def deposit_items(cls):
        """
        Deposit all items from inventory into bank.
        
        Bank interface must be open.
        
        """
        tab_resources_empty = False
        tab_equipment_empty = False

        while True:

            if not tab_resources_empty:
                if cls.__open_tab("resources"):
                    if cls.__deposit_items():
                        tab_resources_empty = True
                        continue

            elif not tab_equipment_empty:
                if cls.__open_tab("equipment"):
                    if cls.__deposit_items():
                        tab_equipment_empty = True
                        continue

            elif tab_resources_empty and tab_equipment_empty:
                log.info("No more items to deposit!")
                return True

    @classmethod
    def open_bank_vault(cls):
        """Open bank interface."""
        log.info("Opening bank vault ... ")

        banker = cls.__banker_detect_npc()

        if banker:
            _, coords = banker
            if cls.__banker_open_dialogue(random.choice(coords)):
                if cls.__banker_open_personal_safe():
                    if cls.__bank_vault() == "opened":
                        log.info("Bank vault is open!")
                        return True

        log.error("Failed to open bank vault!")
        return False

    @staticmethod
    def close_bank_vault():
        """Close bank interface."""
        log.info("Closing bank vault ... ")

        x, y = (904, 173)
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            close_icon = pyautogui.pixelMatchesColor(x, y, (255, 255, 255))

            if not close_icon:
                log.info("Successfully closed!")
                return True

        else:
            log.error(f"Failed to close bank vault in '{wait_time}' "
                      "seconds!")
            return False

    @staticmethod
    def inside_or_outside():
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

    @staticmethod
    def recall_potion():
        """
        Check if 'Recall Potion' is available or not.
        
        Make sure the potion is in first slot of second 'Item' row.

        """
        log.info("Checking if 'Recall Potion' is available ... ")
        color = (120, 151, 154)
        px = pyautogui.pixelMatchesColor(664, 725, color, tolerance=20)
        if px:
            log.info("'Recall Potion' is available!")
            return "available"
        else:
            log.info("'Recall Potion' is not available!")
            return "unavailable"

    @staticmethod
    def use_recall_potion():
        """
        Double click 'Recall Potion' in 'Items' bar.
        
        Make sure the potion is in first slot of second 'Items' row.

        """
        log.info("Using 'Recall Potion' ... ")
        x, y = (664, 725)
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click(clicks=2, interval=0.1)
        time.sleep(0.25)

    @classmethod
    def __banker_detect_npc(cls):
        """Detect banker NPC."""
        log.info("Detecting banker ... ")

        start_time = time.time()
        wait_time = 10

        while time.time() - start_time < wait_time:

            screenshot = wc.WindowCapture.gamewindow_capture()
            rectangles, coordinates = dtc.Detection.detect_objects(
                    cls.img_list,
                    cls.img_path,
                    screenshot
                )

            if len(coordinates) > 0:
                log.info("Banker detected!")
                return rectangles, coordinates
            
        else:
            log.error(f"Failed to detect banker in {wait_time} seconds!")
            return False

    @classmethod
    def __deposit_items(cls):
        """Deposit items in opened tab."""
        log.info("Depositing items ... ")

        start_time = time.time()
        wait_time = 300

        while time.time() - start_time < wait_time:

            if not cls.__slot_empty():
                cls.__deposit_item()
            else:
                log.info("Successfully deposited!")
                return True

        else:
            log.error(f"Failed to deposit items in '{wait_time}' seconds!")
            return False

    @classmethod
    def __slot_empty(cls):
        """Check if first inventory slot is empty."""
        empty_slot = cv.imread(data.images.Bank.empty_bank_slot)
        slot_1_region = (684, 249, 53, 55)

        start_time = time.time()
        wait_time = 3 

        while time.time() - start_time < wait_time:

            slot_1 = wc.WindowCapture.custom_area_capture(slot_1_region)
            slot_1 = dtc.Detection.find(slot_1, empty_slot, threshold=0.9)

            if len(slot_1) <= 0:
                return False

        else:
            return True

    @classmethod
    def __open_tab(cls, tab):
        """
        Open specified tab in character's inventory when bank interface 
        is open.
        """
        log.info(f"Opening '{tab}' tab ... ")

        if cls.official_version:
            tabs = {
                "equipment": (703, 206),
                "misc": (730, 206),
                "resources": (758, 206),
                "souls": (786, 206),
                "runes": (813, 206),
                "cards": (843, 206)
            }
        else:
            tabs = {
                "equipment": (817, 206),
                "misc": (844, 206),
                "resources": (870, 206),
            } 

        x, y = tabs[tab][0], tabs[tab][1]
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click()

        if cls.__check_tab_open(tab):
            log.info(f"Successfully opened '{tab}' tab!")
            return True
        else:
            log.info(f"Failed to open '{tab}' tab!")
            return False

    @staticmethod
    def __check_tab_open(tab):
        """
        Check if specified tab is open in character's inventory when
        bank interface is open.
        """
        tab_region = (684, 186, 231, 40)
        tabs = {
            "equipment": data.images.Bank.tab_equipment,
            "misc": data.images.Bank.tab_misc,
            "resources": data.images.Bank.tab_resources,
            "souls": data.images.Bank.tab_souls,
            "runes": data.images.Bank.tab_runes,
            "cards": data.images.Bank.tab_cards
        }

        # Making sure mouse cursor doesn't get in the way of screenshot.
        pyautogui.moveTo(929, 51)

        sc = wc.WindowCapture.custom_area_capture(tab_region)
        img = cv.imread(tabs[tab])
        rects = dtc.Detection.find(sc, img, threshold=0.8)

        if len(rects) <= 0:
            return True
        else:
            return False

    @staticmethod
    def __inventory():
        """Get status of inventory (opened/closed)."""
        # Gray pixels inside inventory.
        px_1 = pyautogui.pixelMatchesColor(424, 273, (81, 74, 60))
        px_2 = pyautogui.pixelMatchesColor(591, 279, (81, 74, 60))
        px_3 = pyautogui.pixelMatchesColor(820, 116, (213, 207, 170))

        if px_1 and px_2 and px_3:
            return "opened"
        else:
            return "closed"

    @staticmethod
    def __bank_vault():
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

    @staticmethod
    def __banker_open_dialogue(banker_coordinates):
        """
        Talk with banker.
        
        Parameters
        ----------
        banker_coordinates : Tuple[int, int]
            Coordinates (x, y) of banker.

        """
        log.info("Talking with banker ... ")

        x, y = banker_coordinates
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click(button="right")

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            dialogue = pyautogui.pixelMatchesColor(333, 322, (255, 255, 206))

            if dialogue:
                log.info("Successfully started dialogue!")
                return True
        
        else:
            log.error(f"Failed to start dialogue in {wait_time} seconds!")
            return False

    @staticmethod
    def __banker_open_personal_safe():
        """Select first option during dialogue with banker."""
        log.info("Selecting option 'Consult your personal safe' ... ")

        pyautogui.moveTo(294, 365, duration=0.15)
        pyautogui.click()

        wait_time = 3
        click_time = time.time()

        while time.time() - click_time < wait_time:

            dialogue = pyautogui.pixelMatchesColor(333, 322, (255, 255, 206))

            if not dialogue:
                log.info("Successfully selected!")
                return True
        
        else:
            log.error(f"Failed to select option in {wait_time} seconds!")
            return False

    @staticmethod
    def __deposit_item():
        """Move mouse to first inventory slot and double-click."""
        mouse_pos = pyautogui.position()
        slot = (710, 275)

        if mouse_pos != slot:
            pyautogui.moveTo(slot[0], slot[1], duration=0.15)

        pyautogui.keyDown("ctrl")
        pyautogui.click(clicks=2, interval=0.1)
        pyautogui.keyUp("ctrl")

    @staticmethod
    def __calculate_pods():
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
