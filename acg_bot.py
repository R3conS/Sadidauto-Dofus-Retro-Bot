"""Amakna Castle Gobballs script."""

import threading
import time
import os
import random
from typing import NoReturn, Tuple

import cv2 as cv
import pyautogui

from detection import Detection
from window_capture import WindowCapture
from threading_tools import ThreadingTools


class ImageData:
    """Holds image data."""

    test_monster_images_path = "test_monster_images\\"
    test_monster_images_list = ["test_1.jpg", "test_2.jpg", 
                                "test_3.jpg", "test_4.jpg"]

    acg_images_path = "monster_images\\amakna_castle_gobballs\\"
    acg_images_list = [
        "Gobball_BL_1.jpg", "Gobball_BR_1.jpg", 
        "Gobball_TL_1.jpg", "Gobball_TR_1.jpg",
        "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg",
        "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
        "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg",
        "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
    ]


class MapData:
    """Holds map data."""

    acg = [
        {"3,-9": {"top": (  None  ), "bottom": (500, 580),
                 "left": (  None  ), "right" : (900, 310),
                 "cell": (395, 290)}},
        {"4,-9": {"top": (  None  ), "bottom": (500, 580),
                 "left": (30 , 310), "right" : (900, 275),
                 "cell": (  None  )}},
        {"5,-9": {"top": (  None  ), "bottom": (435, 580),
                 "left": (30 , 270), "right" : (  None  ),
                 "cell": (395, 395)}},
        {"3,-8": {"top": (500 , 70), "bottom": (  None  ),
                 "left": (  None  ), "right" : (900, 310),
                 "cell": (330, 290)}},
        {"4,-8": {"top": (500 , 70), "bottom": (  None  ),
                 "left": (30 , 275), "right" : (900, 310),
                 "cell": (  None  )}},
        {"5,-8": {"top": (430 , 70), "bottom": (  None  ),
                 "left": (30 , 310), "right" : (  None  ),
                 "cell": (330, 325)}},
    ]


class BotState:
    """Bot states enum."""

    INITIALIZING = "INITIALIZING"
    SEARCHING = "SEARCHING"
    ATTACKING = "ATTACKING"
    PREPARATION = "PREPARATION"
    IN_COMBAT = "IN_COMBAT"
    CHANGING_MAP = "CHANGING_MAP"


class Bot:
    """
    Main bot logic.
    
    Methods
    ----------  
    Bot_Thread_start()
        Start bot thread.
    Bot_Thread_stop()
        Stop bot thread.

    """

    # Constants.
    # Time to wait after clicking on a monster. How long script will 
    # keep chacking if the monster was successfully attacked.
    __WAIT_AFTER_ATTACKING = 10
    # Time to wait after clicking ready in 'BotState.PREPARATION'. How 
    # long script will keep chacking if combat was started successfully.
    __WAIT_COMBAT_START = 10
    # Time to wait before checking again if the 'Fight Results' window 
    # was properly closed in 'BotState.IN_COMBAT'.
    __WAIT_WINDOW_CLOSED = 3
    # Time to wait before clicking on yellow 'sun' to change maps.
    # Must wait when moving in 'bottom' direction, because 'Dofus' GUI 
    # blocks the sun otherwise.
    __WAIT_SUN_CLICK = 0.5
    # Time to wait AFTER clicking on yellow 'sun' to change maps. 
    # Determines how long to wait for character to change maps after 
    # clicking on yellow 'sun'.
    __WAIT_CHANGE_MAP = 10
    # Time to wait for map to load after a successful map change. 
    # Determines how long script will wait after character moves to a 
    # new map. The lower the number, the higher the chance that on a 
    # slower machine 'SEARCHING' state will act too fast & try to search 
    # for monsters on a black "LOADING MAP" screen. This waiting time 
    # allows the black loading screen to disappear.
    __WAIT_MAP_LOADING = 1

    # Private attributes.
    # Pyautogui mouse movement duration. Default is '0.1' as per docs.
    __move_duration = 0.15
    
    # Threading attributes.
    # 'Bot_Thread' threading attributes.
    __Bot_Thread_stopped = True
    __Bot_Thread_thread = None
    # 'Window_VisualDebugOutput_Thread' threading attributes.
    __Window_VisualDebugOutput_Thread_stopped = True
    __Window_VisualDebugOutput_Thread_thread = None

    # State attributes.
    # 'BotState.SEARCHING' attributes.
    __obj_rects = []
    __obj_coords = []
    # 'BotState.ATTACKING' attributes.
    # Failed attack attempts allowed before searching for monsters.
    __attack_attempts_allowed = 3
    # 'BotState.PREPARATION' attributes.
    __botstate_preparation_current_map = None
    # 'BotState.CHANGING_MAP' attributes.
    __botstate_changing_map_current_map = None

    # Objects.
    __threading_tools = ThreadingTools()
    __window_capture = WindowCapture()
    __detection = Detection()

    def __init__(self, 
                 objects_list: list[str] = ImageData.acg_images_list,
                 objects_path: str = ImageData.acg_images_path,
                 debug_window: bool = False,
                 detection_threshold: float = 0.6,
                 bot_state: str = BotState.INITIALIZING):
        """
        Constructor

        Parameters
        ----------
        objects_list : list[str], optional
            `list` of monster images. Defaults to 
            `ImageData.acg_images_list`.
        objects_path : str, optional
            Path to image folder. Defaults to 
            `ImageData.acg_images_path`.
        debug_window : bool, optional
            Whether to open visual debug window. Defaults to: `False`.
        detection_threshold : bool, optional
            Controls threshold value for `detect_objects()` in
            `BotState.SEARCHING`. Defaults to 0.6.
        bot_state : str, optional
            Current state of bot. Defaults to: `BotState.INITIALIZING`.

        """
        self.__objects_list = objects_list
        self.__objects_path = objects_path
        self.__debug_window = debug_window
        self.__detection_threshold = detection_threshold
        self.__state = bot_state

#----------------------------------------------------------------------#
#-------------------------------METHODS--------------------------------#
#----------------------------------------------------------------------#

    def __check_if_map_in_database(self, 
                                 map: str, 
                                 database: list[dict]) \
                                 -> bool:
        """
        Check if map is in database.

        Parameters
        ----------
        map : str
            Map to check.
        database : list[dict]
            Database to check in.

        Returns
        ----------
        True : bool
            If `map` is in `database`.
        False : bool
            If `map` is NOT in `database`.

        """
        maps = []
        for _, value in enumerate(database):
            for key in value.keys():
                maps.append(key)

        if map not in maps:
            return False

        return True

    def __get_current_map_coordinates(self) -> bool | str:
        """
        Get current map's coordinates.
        
        Returns
        ----------
        map_coords : str
            Map coordinates as a `str`.
        False : bool
            If map wasn't detected.

        """
        # Get a screenshot of coordinates on minimap. Moving mouse
        # over the red area on the minimap for the black map tooltip
        # to appear.
        pyautogui.moveTo(517, 680)
        screenshot = self.__window_capture.custom_area_capture(
                capture_region=self.__window_capture.MAP_DETECTION_REGION,
                conversion_code=cv.COLOR_RGB2GRAY,
                interpolation_flag=cv.INTER_LINEAR,
                scale_width=215,
                scale_height=200
            )
        # Moving mouse off the red area on the minimap in case a new 
        # screenshot is required for another detection.
        pyautogui.move(20, 0)

        # Get map coordinates as a string.
        r_and_t, _, _ = self.__detection.detect_text_from_image(screenshot)
        try:
            map_coords = r_and_t[0][1]
            map_coords = map_coords.replace(".", ",")
        except IndexError:
            return False

        return map_coords

#----------------------------------------------------------------------#
#--------------------------BOT STATE METHODS---------------------------#
#----------------------------------------------------------------------#

    def __botstate_initializing(self):
        """Initializing state logic."""
        # Starting 'WindowCapture_Thread' thread. 
        self.__window_capture.WindowCapture_Thread_start()

        # Waiting for 'WindowCapture_Thread' to complete at least one 
        # cycle before continuing script execution. If this is omitted, 
        # script will reach 'self.__detection.detect_objects()' method 
        # in 'SEARCHING' state faster than the 'WindowCapture_Thread' 
        # can make the first screenshot for detection. Will throw out an 
        # error: (-215:Assertion failed) in 'cv::matchTemplate'.
        while self.__window_capture.screenshot_for_obj_detection is None:
            continue

        # Starts 'Window_VisualDebugOutput_Thread'.
        if self.__debug_window:
            self.__Window_VisualDebugOutput_Thread_start()

        print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ... ")
        self.__state = BotState.SEARCHING

    def __botstate_searching(self):
        """Searching state logic."""
        print(f"[INFO] Searching for monsters ... ")
        self.__obj_rects, self.__obj_coords = self.__detection.detect_objects(
                self.__objects_list, 
                self.__objects_path, 
                self.__window_capture.screenshot_for_obj_detection,
                threshold=self.__detection_threshold
            )

        # If monsters were detected.
        if len(self.__obj_coords) > 0:
            print(f"[INFO] Monsters found at: {self.__obj_coords}!")
            print("[INFO] Changing 'BotState' to: "
                  f"'{BotState.ATTACKING}' ... ")
            self.__state = BotState.ATTACKING
                
        # If monsters were NOT detected.
        elif len(self.__obj_coords) <= 0:
            print("[INFO] Couldn't find any monsters!")
            print("[INFO] Changing 'BotState' to: "
                  f"'{BotState.CHANGING_MAP}' ... ")
            self.__state = BotState.CHANGING_MAP

    def __botstate_attacking(self):
        """Attacking state logic."""
        # Flow control variables.
        attack_successful = False
        attack_attempts_allowed = 0
        attack_attempts_total = 0

        # Allowing character to fail an attack no more than 
        # 'self.attack_attempts_allowed' times.
        if len(self.__obj_coords) > self.__attack_attempts_allowed:
            attack_attempts_allowed = self.__attack_attempts_allowed
        else:
            attack_attempts_allowed = len(self.__obj_coords)

        # Looping through detected monster coordinates.
        for coords in self.__obj_coords:

            x_coord, y_coord = coords

            # Separating moving mouse and clicking into two actions, 
            # because otherwise it sometimes right clicks too early,
            # causing the character to fail an attack.
            print(f"[INFO] Attacking monster at: {coords} ... ")
            pyautogui.moveTo(x=x_coord, 
                             y=y_coord,
                             duration=self.__move_duration)
            pyautogui.click(button="right")

            # This loop will keep trying to find 'status_images' that 
            # confirm if the monster was attacked succesfully. The wait 
            # time is controlled by '__WAIT_AFTER_ATTACKING'.
            # If images were detected, combat was started successfully 
            # and state will be changed to 'PREPARATION'.
            # If images were not detected within the time specified, 
            # the 'while' loop will break to start next 'for' loop
            # iteration and try next coordinates.
            # If char. fails to attack 'self.attack_attempts_allowed' 
            # times, 'BotState' will be changed to 'SEARCHING'.
            attack_time = time.time()
            while True:

                cc_icon = self.__detection.find(
                            self.__window_capture.screenshot_for_obj_detection, 
                            "status_images\\PREPARATION_state_verifier_1.jpg"
                        )
                ready_button = self.__detection.find(
                            self.__window_capture.screenshot_for_obj_detection, 
                            "status_images\\PREPARATION_state_verifier_2.jpg"
                        )
                
                if time.time() - attack_time > self.__WAIT_AFTER_ATTACKING:
                    print(f"[INFO] Failed to attack monster at: {coords}!")
                    print("[INFO] Trying the next coordinates ... ")
                    attack_attempts_total += 1
                    break
                elif len(cc_icon) > 0 and len(ready_button) > 0:
                    print("[INFO] Successfully attacked monster at: "
                          f"{coords}!")
                    print("[INFO] Changing 'BotState' to: "
                          f"'{BotState.PREPARATION}' ... ")
                    self.__state = BotState.PREPARATION
                    attack_successful = True
                    break

            if attack_successful:
                break
            elif (not attack_successful and
                  attack_attempts_allowed == attack_attempts_total):
                print("[INFO] Failed to start combat "
                      f"'{attack_attempts_total}' time(s)!")
                print("[INFO] Changing 'BotState' to: "
                      f"'{BotState.SEARCHING}' ... ")
                self.__state = BotState.SEARCHING
                break

    def __botstate_preparation(self):
        """Preparation state logic."""
        # Resetting both values, so the 'output_image' in 
        # '__Window_VisualDebugOutput_Thread_run()' is clean.
        self.__obj_rects = []
        self.__obj_coords = []

        # Detect current map.
        if self.__botstate_preparation_detect_map():
            # Move character to starting cell.
            if self.__botstate_preparation_move_char_on_cell():
                # Start combat.
                if self.__botstate_preparation_start_combat():
                    self.__state = BotState.IN_COMBAT

    def __botstate_preparation_detect_map(self) -> bool | NoReturn:
        """
        Detect current map.
        
        Returns
        ----------
        True : bool
            If map was detected successfully.
        NoReturn
            Exit program if map wasn't detected within
            `wait_time_before_exit` seconds.
        
        """
        start_time = time.time()
        wait_time_before_exit = 10

        while time.time() - start_time < wait_time_before_exit:
            map_coords = self.__get_current_map_coordinates()
            if map_coords:
                if not self.__check_if_map_in_database(map_coords, 
                                                       MapData.acg):
                    print("[ERROR] Fatal error in "
                        "'__botstate_preparation_detect_map()'!")
                    print(f"[ERROR] Map ({map_coords}) doesn't exist "
                        "in database!")
                    print("[ERROR] Exiting ... ")
                    os._exit(1)
                else:
                    self.__botstate_preparation_current_map = map_coords
                    return True
        else:
            print("[ERROR] Fatal error in "
                  "'__botstate_preparation_detect_map()'!")
            print("[ERROR] Exceeded detection time limit of "
                  f"{wait_time_before_exit} second(s)!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __botstate_preparation_move_char_on_cell(self):
        """Move character to a correct cell before starting combat."""
        click_attempts_total = 0
        click_attempts_allowed = 3

        # Get current map's starting cell coordinates.
        for _, value in enumerate(MapData.acg):
            for i_key, i_value in value.items():
                if self.__botstate_preparation_current_map == i_key:
                    if i_value["cell"] is not None:
                        cell_x = i_value["cell"][0]
                        cell_y = i_value["cell"][1]
                    else:
                        print("[INFO] Character is standing on correct cell!")
                        return True

        while True:

            # Move the cursor to starting cell coordinates.
            pyautogui.moveTo(cell_x, cell_y, duration=self.__move_duration)

            # Take a screenshot before clicking on starting cell.
            before_click = self.__window_capture.area_around_mouse_capture(15)

            # Clicking on the cell.
            print(f"[INFO] Clicking on starting cell: {cell_x, cell_y} ... ")
            pyautogui.click()
            click_attempts_total += 1

            # Take a screenshot after clicking on starting cell.
            after_click = self.__window_capture.area_around_mouse_capture(15)

            # Comparing the two screenshots
            sc_compared = self.__detection.find(before_click, 
                                              after_click,
                                              threshold=0.96)

            # Controls failed click attempts.
            if click_attempts_total >= click_attempts_allowed:
                print("[ERROR] Failed to select starting cell!")
                print("[ERROR] Exiting ... ")
                os._exit(1)

            # If there is NO difference between two screenshots, 
            # it means character is not standing on the correct cell.
            elif len(sc_compared) > 0:
                print("[INFO] Failed to move character to starting cell!")
                continue

            # If there IS a difference between two screenshots, 
            # it means character is standing on the correct cell.
            elif len(sc_compared) <= 0:
                print("[INFO] Character is standing on correct cell!")
                return True

    def __botstate_preparation_start_combat(self):
        """Click ready to start combat."""
        ready_button_clicked = False

        while True:

            ready_button_icon = self.__detection.get_click_coords(
                    self.__detection.find(
                            self.__window_capture.screenshot_for_obj_detection, 
                            "status_images\\PREPARATION_state_verifier_2.jpg",
                            threshold=0.8
                        )
                    )

            # If 'READY' button was found.
            if len(ready_button_icon) > 0 and not ready_button_clicked:

                print("[INFO] Clicking 'READY' ... ")
                pyautogui.moveTo(x=ready_button_icon[0][0],
                                 y=ready_button_icon[0][1],
                                 duration=self.__move_duration)
                pyautogui.click()
                # Moving the mouse off the 'READY' button in case it 
                # needs to be detected again.
                pyautogui.move(0, 80)
                click_time = time.time()
                ready_button_clicked = True 

            # Checking if combat started after 'READY' was clicked.
            if ready_button_clicked:

                cc_icon = self.__detection.find(
                        self.__window_capture.screenshot_for_obj_detection, 
                        "status_images\\IN_COMBAT_state_verifier_1.jpg", 
                        threshold=0.8
                    )
                ap_icon = self.__detection.find(
                        self.__window_capture.screenshot_for_obj_detection, 
                        "status_images\\IN_COMBAT_state_verifier_2.jpg", 
                        threshold=0.8
                    )
                mp_icon = self.__detection.find(
                        self.__window_capture.screenshot_for_obj_detection, 
                        "status_images\\IN_COMBAT_state_verifier_3.jpg", 
                        threshold=0.8
                    )
                
                if time.time() - click_time > self.__WAIT_COMBAT_START:
                    print("[INFO] Failed to start combat!")
                    print("[INFO] Retrying ... ")
                    ready_button_clicked = False
                    continue

                if len(cc_icon) > 0 and len(ap_icon) > 0 and len(mp_icon) > 0:
                    print("[INFO] Successfully started combat!")
                    print("[INFO] Changing 'BotState' to: "
                          f"'{BotState.IN_COMBAT}' ... ")
                    return True

    def __botstate_in_combat(self):
        """Combat state logic."""
        # TO DO
        # Fighting Logic
        self.__botstate_in_combat_check_end_of_fight()

    def __botstate_in_combat_check_end_of_fight(self):
        """Check if combat has ended and close fight results window."""
        close_button_clicked = False

        while True:

            close_button_icon = self.__detection.get_click_coords(
                    self.__detection.find(
                            self.__window_capture.screenshot_for_obj_detection,
                            "status_images\\END_OF_COMBAT_verifier_1.jpg",
                            threshold=0.8
                        )
                    )
            cc_icon = self.__detection.get_click_coords(
                    self.__detection.find(
                            self.__window_capture.screenshot_for_obj_detection, 
                            "status_images\\END_OF_COMBAT_verifier_2.jpg"
                        )
                    )
            
            # If the close button is detected.
            if len(close_button_icon) > 0 and not close_button_clicked:
                print("[INFO] Combat has ended!")
                print("[INFO] Closing 'Fight Results' window ... ")
                # Separating moving mouse and clicking into two actions, 
                # because otherwise it sometimes right clicks too early.
                pyautogui.moveTo(x=close_button_icon[0][0], 
                                 y=close_button_icon[0][1], 
                                 duration=self.__move_duration)
                pyautogui.click()
                click_time = time.time()
                close_button_clicked = True
                # Moving mouse off the 'Close' button in case it needs 
                # to be detected again.
                pyautogui.move(100, 0)
                continue

            if close_button_clicked:
                # Checking if the 'Fight Results' window was closed.
                if (len(close_button_icon) > 0 and
                    time.time() - click_time > self.__WAIT_WINDOW_CLOSED):
                    print("[INFO] Failed to close 'Fight Results' window!")
                    print("[INFO] Retrying ... ")
                    close_button_clicked = False
                
                elif len(close_button_icon) <= 0 and len(cc_icon) <= 0:
                    print("[INFO] Successfully closed 'Fight Results' window!")
                    print("[INFO] Changing 'BotState' to: "
                          f"'{BotState.SEARCHING}' ... ")
                    self.__state = BotState.SEARCHING
                    break

    def __botstate_changing_map(self):
        """Changing map state logic."""
        if self.__botstate_changing_map_detect_map():
            if self.__botstate_changing_map_change_map():
                self.__state = BotState.SEARCHING

    def __botstate_changing_map_detect_map(self) -> bool | NoReturn:
        """
        Detect current map.
        
        Returns
        ----------
        True : bool
            If map was detected successfully.
        NoReturn
            Exit program if map wasn't detected within
            `wait_time_before_exit` seconds.

        """
        start_time = time.time()
        wait_time_before_exit = 10

        while time.time() - start_time < wait_time_before_exit:
            map_coords = self.__get_current_map_coordinates()
            if map_coords:
                print(f"[INFO] Character is on map: ({map_coords}) ... ")
                if not self.__check_if_map_in_database(map_coords,
                                                       MapData.acg):
                    print("[ERROR] Fatal error in "
                          "'__botstate_changing_map_detect_map()'!")
                    print(f"[ERROR] Map ({map_coords}) doesn't exist "
                          "in database!")
                    print("[ERROR] Exiting ... ")
                    os._exit(1)
                else:
                    self.__botstate_changing_map_current_map = map_coords
                    return True
        else:
            print("[ERROR] Fatal error in "
                  "'__botstate_changing_map_detect_map()'!")
            print("[ERROR] Exceeded detection time limit of "
                  f"{wait_time_before_exit} second(s)!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __botstate_changing_map_get_move_coords(self) \
                                                -> Tuple[Tuple[int, int], str]:
        """
        Get move (x, y) coordinates and move choice.

        Returns
        ----------
        move_coords: tuple[int, int]
            (x, y) coordinates to click on for map change.
        move_choice: str
            Move direction.

        """
        # List of valid directions for moving to change maps.
        directions = ["top", "bottom", "left", "right"]

        # Loop gets current map's moving directions that are not 'None' 
        # and current map's index in 'MapData'.
        possible_directions = []
        map_index = None
        for index, value in enumerate(MapData.acg):
            for i_key, i_value in value.items():
                if self.__botstate_changing_map_current_map == i_key:
                    for j_key, j_value in i_value.items():
                        if j_value is not None and j_key in directions:
                            possible_directions.append(j_key)
                            map_index = index

        # Generating a random choice from 'possible_directions'.
        move_choice = random.choice(possible_directions)

        # Getting (x, y) coordinates.
        move_coords = MapData.acg[map_index]\
                                 [self.__botstate_changing_map_current_map]\
                                 [move_choice]

        return move_coords, move_choice

    def __botstate_changing_map_change_map(self) -> bool | NoReturn:
        """
        Change maps.

        - Gets coordinates to click on for map change. 
        - Clicks.
        - Starts comparing current map's coordinates to global
        coordinates generated by `__botstate_changing_map_detect_map()`,
        has `__WAIT_CHANGE_MAP` seconds for comparison.
        - If coordinates are the same after `__WAIT_CHANGE_MAP` seconds
        of comparing, increments `change_attempts_total`, gets new click
        coordinates and tries to change maps again.
        - If coordinates are different, means map change was successful.

        Returns
        ----------
        True : bool
            If map change was a successful.
        NoReturn
            Exit program if map change wasn't successful after 
            `change_attempts_allowed` tries.

        """
        change_attempts_allowed = 3
        change_attempts_total = 0

        while change_attempts_total < change_attempts_allowed:
            # Changing maps.
            coords, choice = self.__botstate_changing_map_get_move_coords()
            print(f"[INFO] Clicking on: {(coords[0], coords[1])} to move "
                  f"'{choice}' ... ")
            pyautogui.keyDown('e')
            pyautogui.moveTo(coords[0], coords[1])
            if choice == "bottom":
                time.sleep(self.__WAIT_SUN_CLICK)
            pyautogui.click()
            pyautogui.keyUp('e')
            change_attempts_total += 1
            start_time = time.time()

            while time.time() - start_time < self.__WAIT_CHANGE_MAP:
                map_coords = self.__get_current_map_coordinates()
                if (self.__botstate_changing_map_current_map != map_coords 
                    and map_coords):
                    print(f"[INFO] Waiting '{self.__WAIT_MAP_LOADING}' "
                          "second(s) for map to load!")
                    time.sleep(self.__WAIT_MAP_LOADING)
                    print("[INFO] Map changed successfully!")
                    print("[INFO] Changing 'BotState' to: "
                        f"'{BotState.SEARCHING}' ... ")
                    return True
        else:
            print("[ERROR] Fatal error in "
                  "'__botstate_changing_map_change_map()'!")
            print("[ERROR] Too many failed attemps to change map!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

#----------------------------------------------------------------------#
#------------------------MAIN THREAD OF CONTROL------------------------#
#----------------------------------------------------------------------#

    def __Bot_Thread_run(self):
        """Execute this code while bot thread is alive."""
        while not self.__Bot_Thread_stopped:

            # The bot always starts up in this (INITIALIZING) state. 
            if self.__state == BotState.INITIALIZING:
                self.__botstate_initializing()

            # Handles monster detection.
            elif self.__state == BotState.SEARCHING:
                self.__botstate_searching()

            # Handles attacking found monsters.
            elif self.__state == BotState.ATTACKING:
                self.__botstate_attacking()

            # Handles combat preparation actions.
            elif self.__state == BotState.PREPARATION:
                self.__botstate_preparation()

            # Handles combat actions.
            elif self.__state == BotState.IN_COMBAT:
                self.__botstate_in_combat()
                        
            # Handles map changing actions.
            elif self.__state == BotState.CHANGING_MAP:
                self.__botstate_changing_map()
                      
#----------------------------------------------------------------------#
#--------------------------THREADING METHODS---------------------------#
#----------------------------------------------------------------------#

    def Bot_Thread_start(self):
        """Start bot thread."""
        self.__Bot_Thread_stopped = False
        self.__Bot_Thread_thread = threading.Thread(
                target=self.__Bot_Thread_run
            )
        self.__Bot_Thread_thread.start()
        self.__threading_tools.wait_thread_start(self.__Bot_Thread_thread)

    def Bot_Thread_stop(self):
        """Stop bot thread."""
        self.__Bot_Thread_stopped = True
        self.__window_capture.WindowCapture_Thread_stop()
        self.__Window_VisualDebugOutput_Thread_stop()
        self.__threading_tools.wait_thread_stop(self.__Bot_Thread_thread)

#----------------------------------------------------------------------#

    def __Window_VisualDebugOutput_Thread_start(self):
        """Start VisualDebugOutput thread."""
        self.__Window_VisualDebugOutput_Thread_stopped = False
        self.__Window_VisualDebugOutput_Thread_thread = threading.Thread(
                target=self.__Window_VisualDebugOutput_Thread_run
            )
        self.__Window_VisualDebugOutput_Thread_thread.start()
        self.__threading_tools.wait_thread_start(
                self.__Window_VisualDebugOutput_Thread_thread
            )

    def __Window_VisualDebugOutput_Thread_stop(self):
        """Stop VisualDebugOutput thread."""
        self.__Window_VisualDebugOutput_Thread_stopped = True
        self.__threading_tools.wait_thread_stop(
                self.__Window_VisualDebugOutput_Thread_thread
            )
        
    def __Window_VisualDebugOutput_Thread_run(self):
        """Execute this code while thread is alive."""
        while not self.__Window_VisualDebugOutput_Thread_stopped:

            loop_time = time.time()

            # Waiting for first screenshot to come through, otherwise
            # will throw an exception: (-215:Assertion failed)
            # size.width>0 && size.height>0 in function 'cv::imshow'.
            if self.__window_capture.screenshot_for_VDO_Thread is None:
                continue

            # Draw boxes around detected monsters.
            output_image = self.__detection.draw_rectangles(
                    self.__window_capture.screenshot_for_VDO_Thread, 
                    self.__obj_rects
                )

            # Displaying the processed image.
            cv.imshow("Visual Debug Window", output_image)

            # Press 'q' while the DEBUG window is focused to exit.
            if cv.waitKey(1) == ord("q"):
                # Hard exiting and force killing all threads (not clean)
                cv.destroyAllWindows()
                print("Done")
                os._exit(1)

            # Uncomment to display FPS in terminal (spams terminal).
            # print(f"FPS {round(1 / (time.time() - loop_time), 2)}")
            loop_time = time.time()

#----------------------------------------------------------------------#
