import threading
import pyautogui
import time
import os
import cv2 as cv
import random
from detection import Detection
from window_capture import Window_Capture
from threading_tools import Threading_Tools


class ImageData:
    

    test_monster_images_path = "test_monster_images\\"
    test_monster_images_list = ["test_1.jpg", "test_2.jpg", "test_3.jpg", "test_4.jpg"]

    amakna_castle_gobballs_map_images_path = "map_images\\amakna_castle_gobballs\\"
    amakna_castle_gobballs_map_images_list = ["3,-8.jpg", "3,-9.jpg", "4,-8.jpg", "4,-9.jpg", "5,-8.jpg", "5,-9.jpg"]

    amakna_castle_gobballs_images_path = "monster_images\\amakna_castle_gobballs\\"
    amakna_castle_gobballs_images_list = [
                                        "Gobball_BL_1.jpg", "Gobball_BR_1.jpg", "Gobball_TL_1.jpg", "Gobball_TR_1.jpg",
                                        "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg", "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
                                        "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg", "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
                                         ]


class MapData:


    amakna_castle_gobballs = [

        {"3,-9": {"top": (  None  ), "bottom": (500, 580), "left": (  None  ), "right": (900, 310), "cell": (395, 290)} },
        {"4,-9": {"top": (  None  ), "bottom": (500, 580), "left": (30 , 310), "right": (900, 275), "cell": (230, 310)} },
        {"5,-9": {"top": (  None  ), "bottom": (435, 580), "left": (30 , 270), "right": (  None  ), "cell": (395, 395)} },
        {"3,-8": {"top": (500 , 70), "bottom": (  None  ), "left": (  None  ), "right": (900, 310), "cell": (330, 290)} },
        {"4,-8": {"top": (500 , 70), "bottom": (  None  ), "left": (30 , 275), "right": (900, 310), "cell": (265, 290)} },
        {"5,-8": {"top": (430 , 70), "bottom": (  None  ), "left": (30 , 310), "right": (  None  ), "cell": (330, 325)} },

    ]


class BotState:


    INITIALIZING = "INITIALIZING"
    SEARCHING = "SEARCHING"
    ATTACKING = "ATTACKING"
    PREPARATION = "PREPARATION"
    IN_COMBAT = "IN_COMBAT"
    CHANGING_MAP = "CHANGING_MAP"


class DofusBot:


    # Constants.
    # Time to wait after clicking on a monster. Determines how long script will keep chacking (in BotState.ATTACKING) if the monster was successfully attacked.
    WAIT_TIME_AFTER_ATTACKING_MONSTER = 10
    # Time to wait after clicking ready in 'BotState.PREPARATION'. Determines how long script will keep chacking if combat was started successfully.
    WAIT_TIME_COMBAT_START = 10
    # Time to wait before checking again if the 'Fight Results' window was properly closed in 'BotState.IN_COMBAT'.
    WAIT_TIME_FIGHT_RESULT_WINDOW_CLOSED = 3
    # Time to wait before clicking on yellow 'sun' to change maps.
    WAIT_TIME_CHANGING_MAP_CLICK = 0.5
    # Time to wait AFTER clicking on yellow 'sun' to change maps. Determines how long script will wait for character to change maps.
    WAIT_TIME_BEFORE_TRY_CHANGE_MAP_AGAIN = 10
    # Time to wait for map to load after a successful map change. Determines how long script will wait after character moves to a new map.
    # The lower the number, the higher the chance that on a slower machine 'SEARCHING' state will act too fast & try to search for monsters
    # on a black "LOADING MAP" screen. This waiting time allows the black loading screen to disappear.
    WAIT_TIME_MAP_LOADING = 1


    # 'DofusBot_Thread' threading properties.
    DofusBot_Thread_stopped = True
    DofusBot_Thread_thread = None


    # 'Window_VisualDebugOutput_Thread' threading properties.
    Window_VisualDebugOutput_Thread_stopped = True
    Window_VisualDebugOutput_Thread_lock = None
    Window_VisualDebugOutput_Thread_thread = None
    Window_VisualDebugOutput_window = None


    # Properties.
    objects_to_detect_list = None
    objects_to_detect_path = None
    # Threshold controller for 'detect_objects()'
    detection_threshold = None
    # Used in 'detect_objects()'.
    detected_object_rectangles = []
    detected_object_click_points = []
    # Pyautogui mouse movement duration. Default is '0.1' as per docs. Basically instant.
    move_duration = 0.15


    # 'BotState.ATTACKING' properties.
    # How many attemps to fail an attack are allowed before searching for monsters again.
    attacking_state_attack_attempts_allowed = 3


    # 'BotState.PREPARATION' properties.
    preparation_state_cell_x_coordinate = None
    preparation_state_cell_y_coordinate = None
    preparation_state_current_map_detected_successfully = False
    preparation_state_cell_selected_successfully = False
    # Keeps count of how many times script tried to move character to the starting cell.
    preparation_state_cell_click_attempts_total = 0
    # How many attemps at clicking on the starting cell are allowed before exiting.
    preparation_state_cell_click_attempts_allowed = 3


    # 'BotState.CHANGING_MAP' properties.
    # Keeps count of how many times script tried to change maps.
    changing_map_state_change_map_attempts_total = 0
    # How many attemps to change maps are allowed before exiting.
    changing_map_state_change_map_attempts_allowed = 3
    # Controls flow.
    changing_map_state_current_map_detected_successfully = False

    
    def __init__(self, objects_to_detect_list, objects_to_detect_path, debug_window=False, detection_threshold=0.6):

        # Loading monster/object images.
        self.objects_to_detect_list = objects_to_detect_list
        self.objects_to_detect_path = objects_to_detect_path

        # If 'True', will allow bot to run 'Window_VisualDebugOutput_Thread_start' which opens an 'OpenCV' debug window.
        self.Window_VisualDebugOutput_window = debug_window

        # Controls detection threshold value in methods like 'detection.detect_objects()' and 'detection.find()'.
        # Anything below '0.6' seems to give a lot of false results.
        self.detection_threshold = detection_threshold

        # Default state of the bot at the start.
        self.state = BotState.INITIALIZING

        # Initializing 'Threading_Tools()' object. Holds various custom threading methods.
        self.threading_tools = Threading_Tools()

        # Initializing 'Window_Capture()' object. Handles screenshotting the game window.
        self.window_capture = Window_Capture()

        # Initializing 'Detection()' object & it's 'threading.Lock()' object.
        self.detection = Detection()


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------METHODS---------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#


    # Checks if provided maps data is in database.
    # Map - must be a string
    # Database - list of dictionaries.
    def check_if_map_present_in_database(self, map, database):

        listas = []
        
        for _, value in enumerate(database):

            for key in value.keys():

                listas.append(key)

        if map not in listas:
            return False

        return True


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------MAIN THREAD OF CONTROL---------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#


    def DofusBot_Thread_run(self):

        while not self.DofusBot_Thread_stopped:

            # The bot always starts up in this (INITIALIZING) state. 
            # Starts 'Window_Capture_Thread', if needed starts the 'Window_VisualDebugOutput_Thread' and changes it's state to 'SEARCHING'.
            if self.state == BotState.INITIALIZING:

                # Starting the 'Window_Capture_Thread' thread to start screenshotting the game window. 
                self.window_capture.Window_Capture_Thread_start()

                # Waiting for 'Window_Capture_Thread' to complete at least one cycle before continuing script execution.
                # If this is omitted, script will reach 'self.detection.detect_objects()' method in 'SEARCHING' state faster than the
                # 'Window_Capture_Thread' can make the first screenshot for detection. Will throw out an error like this:
                # (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() && _img.dims() <= 2 in function 'cv::matchTemplate'
                while self.window_capture.screenshot_for_object_detection is None:
                    continue

                # Launches an 'OpenCV' window for debug purposes.
                if self.Window_VisualDebugOutput_window:
                    # Starting' Window_VisualDebugOutput_Thread'.
                    self.Window_VisualDebugOutput_Thread_start()

                print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ...")
                self.state = BotState.SEARCHING


            # This state handles the monster detection.
            # If monsters are detected, the 'BotState' changes to 'ATTACKING'.
            # If nothing is detected, the 'BotState' changes to 'CHANGING_MAP'.
            elif self.state == BotState.SEARCHING:
                    
                    print(f"[INFO] Searching for monsters ... ")

                    self.detected_object_rectangles, self.detected_object_click_points = self.detection.detect_objects(
                                                                                                                      self.objects_to_detect_list, 
                                                                                                                      self.objects_to_detect_path, 
                                                                                                                      self.window_capture.screenshot_for_object_detection,
                                                                                                                      threshold=self.detection_threshold,
                                                                                                                      )

                    # EXECUTE THIS BLOCK IF MONSTERS WERE DETECTED.
                    if len(self.detected_object_click_points) > 0:

                        print(f"[INFO] Monsters found at: {self.detected_object_click_points}!")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.ATTACKING}' ... ")
                        self.state = BotState.ATTACKING
                            
                    # EXECUTE THIS BLOCK IF MONSTERS WERE **NOT** DETECTED.
                    elif len(self.detected_object_click_points) <= 0:

                        print("[INFO] Couldn't find any monsters!")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.CHANGING_MAP}' ... ")
                        self.state = BotState.CHANGING_MAP


            # Handles attacking found monsters by 'SEARCHING' state.
            elif self.state == BotState.ATTACKING:

                attacking_state_attack_successful = False
                attacking_state_attack_attempts_allowed = 0
                attacking_state_attack_attempts_total = 0

                # Allowing script to fail an attack no more than 'self.attacking_state_attack_attempts_allowed' times.
                if len(self.detected_object_click_points) > self.attacking_state_attack_attempts_allowed:
                    attacking_state_attack_attempts_allowed = self.attacking_state_attack_attempts_allowed
                else:
                    attacking_state_attack_attempts_allowed = len(self.detected_object_click_points)

                # Looping through detected monster coordinates.
                for attacking_state_click_points in self.detected_object_click_points:

                    attacking_state_x_coordinate, attacking_state_y_coordinate = attacking_state_click_points

                    # Separating moving mouse and clicking into two actions instead of one, because otherwise it sometimes right clicks too early,
                    # causing the character to fail an attack.
                    print(f"[INFO] Attacking monster at: {attacking_state_click_points} ... ")
                    pyautogui.moveTo(x=attacking_state_x_coordinate, y=attacking_state_y_coordinate, duration=self.move_duration)
                    pyautogui.click(button="right")

                    # This loop will keep trying to find 'status_images' that confirm if the monster was attacked succesfully.
                    # The wait time is controlled by 'WAIT_TIME_AFTER_ATTACKING_MONSTER'.
                    # If images were detected, then combat was started successfully and the bot will change state to 'PREPARATION'.
                    # If images are not detected within the time specified, the 'while' loop will break to start the next 'for' loop iteration
                    # and try the next coordinates.
                    # If character fails to attack 'self.attacking_state_attack_attempts_allowed' times, 'BotState' will be changed to 'SEARCHING'.
                    attack_action_start_time = time.time()
                    while True:

                        cc_icon_attacking_state = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\PREPARATION_state_verifier_1.jpg")
                        ready_button_attacking_state = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\PREPARATION_state_verifier_2.jpg")
                        
                        if time.time() - attack_action_start_time > self.WAIT_TIME_AFTER_ATTACKING_MONSTER:
                            print(f"[INFO] Failed to attack monster at: {attacking_state_click_points}!")
                            print(f"[INFO] Trying the next coordinates ... ")
                            attacking_state_attack_attempts_total += 1
                            break

                        elif len(cc_icon_attacking_state) > 0 and len(ready_button_attacking_state) > 0:
                            print(f"[INFO] Successfully attacked monster at: {attacking_state_click_points}!")
                            print(f"[INFO] Changing 'BotState' to: '{BotState.PREPARATION}' ... ")
                            self.state = BotState.PREPARATION
                            attacking_state_attack_successful = True
                            break

                    if attacking_state_attack_successful:
                        break

                    elif not attacking_state_attack_successful and attacking_state_attack_attempts_allowed == attacking_state_attack_attempts_total:
                        print(f"[INFO] Failed to start combat '{attacking_state_attack_attempts_total}' time(s)!")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ... ")
                        self.state = BotState.SEARCHING
                        break


            # Handles selecting best starting position and starting combat.
            elif self.state == BotState.PREPARATION:

                # Resetting both values to empty lists, so the 'output_image' in 'Window_VisualDebugOutput_Thread_run()' is clean.
                # This will prevent script from drawing rectangles around, or markers on, found objects.
                self.detected_object_rectangles = []
                self.detected_object_click_points = []

                # Execute this block if current map wasn't detected.
                if not self.preparation_state_current_map_detected_successfully:

                    # Gets a screenshot of minimap.
                    preparation_state_screenshot_for_current_map_detection = self.window_capture.map_detection_capture()

                    # Control variables
                    preparation_state_current_map = None
                    
                    # Detects current map.
                    for preparation_state_map_image in ImageData.amakna_castle_gobballs_map_images_list:

                        preparation_state_rectangles = self.detection.find(preparation_state_screenshot_for_current_map_detection, ImageData.amakna_castle_gobballs_map_images_path + preparation_state_map_image, threshold=0.95)

                        if len(preparation_state_rectangles) > 0:
                            print(f"[INFO] Preparing to fight at: ({preparation_state_map_image.rstrip('.jpg')}) ... ")
                            preparation_state_current_map = preparation_state_map_image.rstrip('.jpg')
                            self.preparation_state_current_map_detected_successfully = True
                            break

                # If map was detected successfully, get the map's starting cell coordinates and move character there.
                if self.preparation_state_current_map_detected_successfully:

                    # Gets current map's best starting cell coordinates.
                    while True:

                        if not self.check_if_map_present_in_database(preparation_state_current_map, MapData.amakna_castle_gobballs):
                            print("[ERROR] Fatal error in 'BotState.CHANGING_MAP'!")
                            print(f"[ERROR] Couldn't detect map ({changing_map_state_current_map}) in database!")
                            print("[ERROR] Exiting ... ")
                            os._exit(1)

                        for list_index, value in enumerate(MapData.amakna_castle_gobballs):

                            for i_key, j_value in value.items():

                                if preparation_state_current_map == i_key:

                                    self.preparation_state_cell_x_coordinate = j_value["cell"][0]
                                    self.preparation_state_cell_y_coordinate = j_value["cell"][1]

                        # Moves the cursor to starting cell coordinates.
                        pyautogui.moveTo(self.preparation_state_cell_x_coordinate, self.preparation_state_cell_y_coordinate, duration=self.move_duration)

                        # Taking a screenshot before clicking on the starting cell.
                        preparation_state_screenshot_before_clicking_on_cell = self.window_capture.area_around_mouse_capture(15)

                        # Clicking on the cell.
                        print(f"[INFO] Clicking on the starting cell: {self.preparation_state_cell_x_coordinate, self.preparation_state_cell_y_coordinate} ... ")
                        pyautogui.click()
                        self.preparation_state_cell_click_attempts_total += 1

                        # Taking a screenshot after clicking on the starting cell.
                        preparation_state_screenshot_after_clicking_on_cell = self.window_capture.area_around_mouse_capture(15)

                        # Comparing the two screenshots
                        preparation_state_compare_before_and_after_screenshot = self.detection.find(preparation_state_screenshot_before_clicking_on_cell,
                                                                                                     preparation_state_screenshot_after_clicking_on_cell,
                                                                                                     threshold=0.96)

                        # Controls how many times to try and click on starting cell before exiting.
                        if self.preparation_state_cell_click_attempts_total >= self.preparation_state_cell_click_attempts_allowed:
                            print("[ERROR] Failed to select starting cell in 'BotState.PREPARATION'!")
                            print("[ERROR] Exiting ... ")
                            os._exit(1)

                        # If there is NO difference between two screenshots, it means character is not standing on the correct cell.
                        elif len(preparation_state_compare_before_and_after_screenshot) > 0:
                            print("[INFO] Failed to move character to starting cell!")

                        # If there IS a difference between two screenshots, it means character is standing on the correct cell.
                        elif len(preparation_state_compare_before_and_after_screenshot) <= 0:
                            print("[INFO] Character is standing on the correct cell!")
                            self.preparation_state_cell_selected_successfully = True
                            self.preparation_state_current_map_detected_successfully = False
                            self.preparation_state_cell_click_attempts_total = 0
                            break
                            
                # If character was moved to the starting cell successfully, script will try to start combat by clicking 'Ready'.
                if self.preparation_state_cell_selected_successfully:
                
                    preparation_state_ready_button_click_action = False
                    while True:

                        preparation_state_ready_button_icon = self.detection.get_click_points(self.detection.find(self.window_capture.screenshot_for_object_detection, 
                                                                                                                 "status_images\\PREPARATION_state_verifier_2.jpg",
                                                                                                                 threshold=0.8))

                        # If 'READY' button was found.
                        if len(preparation_state_ready_button_icon) > 0 and not preparation_state_ready_button_click_action:

                            print("[INFO] Clicking 'READY' ... ")
                            pyautogui.moveTo(x=preparation_state_ready_button_icon[0][0], y=preparation_state_ready_button_icon[0][1], duration=self.move_duration)
                            pyautogui.click()
                            # Moving the mouse off the 'READY' button incase script needs to detect it again.
                            pyautogui.move(0, 80)
                            click_ready_action_start_time = time.time()
                            preparation_state_ready_button_click_action = True 

                        # Checking if combat started after 'READY' button was clicked.
                        if preparation_state_ready_button_click_action:

                            preparation_state_cc_icon = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\IN_COMBAT_state_verifier_1.jpg", threshold=0.8)
                            preparation_state_ap_icon = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\IN_COMBAT_state_verifier_2.jpg", threshold=0.8)
                            preparation_state_mp_icon = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\IN_COMBAT_state_verifier_3.jpg", threshold=0.8)
                            
                            if time.time() - click_ready_action_start_time > self.WAIT_TIME_COMBAT_START:
                                print("[INFO] Failed to start combat!")
                                print("[INFO] Retrying ... ")
                                preparation_state_ready_button_click_action = False

                            elif len(preparation_state_cc_icon) > 0 and len(preparation_state_ap_icon) > 0 and len(preparation_state_mp_icon) > 0:
                                print("[INFO] Successfully started combat!")
                                print(f"[INFO] Changing 'BotState' to: '{BotState.IN_COMBAT}' ... ")
                                self.state = BotState.IN_COMBAT
                                self.preparation_state_cell_selected_successfully = False
                                break


            # Handles the combat actions.
            elif self.state == BotState.IN_COMBAT:

                print("[INFO] Combat has started!")
                
                #------------------------------------------------------
                # TO BE CREATED: Combat logic
                #------------------------------------------------------

                # Checking if combat has ended.
                in_combat_state_close_button_click_action = False
                while True:

                    in_combat_state_close_button_icon = self.detection.get_click_points(self.detection.find(
                                                                                                    self.window_capture.screenshot_for_object_detection,
                                                                                                    "status_images\\END_OF_COMBAT_verifier_1.jpg",
                                                                                                    threshold=0.8
                                                                                                    ))

                                                                                                    
                    in_combat_state_cc_icon = self.detection.get_click_points(self.detection.find(
                                                                                        self.window_capture.screenshot_for_object_detection, 
                                                                                        "status_images\\END_OF_COMBAT_verifier_2.jpg"
                                                                                        ))
                    
                    # If both conditions are met the fight has ended.
                    if len(in_combat_state_close_button_icon) > 0 and not in_combat_state_close_button_click_action:
                        print("[INFO] Combat has ended!")
                        print("[INFO] Closing 'Fight Results' window ... ")
                        # Separating moving mouse and clicking into two actions instead of one, because otherwise it sometimes right clicks too early,
                        # causing the character to fail an attack.
                        pyautogui.moveTo(x=in_combat_state_close_button_icon[0][0], y=in_combat_state_close_button_icon[0][1], duration=self.move_duration)
                        pyautogui.click()
                        in_combat_state_close_button_click_timestamp = time.time()
                        in_combat_state_close_button_click_action = True
                        # Moving mouse off of the 'Close' button incase script needs to detect it again.
                        pyautogui.move(100, 0)
                        continue

                    if in_combat_state_close_button_click_action:

                        # Checking if the 'Fight Results' window was closed successfully
                        if len(in_combat_state_close_button_icon) > 0 and time.time() - in_combat_state_close_button_click_timestamp > self.WAIT_TIME_FIGHT_RESULT_WINDOW_CLOSED:
                            print("[INFO] Failed to close 'Fight Results' window!")
                            print("[INFO] Retrying ... ")
                            in_combat_state_close_button_click_action = False
                        
                        elif len(in_combat_state_close_button_icon) <= 0 and len(in_combat_state_cc_icon) <= 0:
                            print("[INFO] Successfully closed 'Fight Results' window!")
                            print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ... ")
                            self.state = BotState.SEARCHING
                            break

                        
            # Handles map changing when bot doesn't detect any monsters.
            elif self.state == BotState.CHANGING_MAP:

                if not self.changing_map_state_current_map_detected_successfully:

                    # Gets a screenshot of minimap.
                    changing_map_state_screenshot_for_current_map_detection = self.window_capture.map_detection_capture()

                    # Detecting current map's coordinates in "changing_map_state_screenshot_for_current_map_detection".
                    changing_map_state_current_map_rectangles_and_text, _, _ = self.detection.ocr_detect_text_from_image(changing_map_state_screenshot_for_current_map_detection)

                    # Storing current map's coordinates.
                    changing_map_state_current_map = changing_map_state_current_map_rectangles_and_text[0][1]

                    # Replacing dots with commas in case a dot is detected instead of a comma.
                    changing_map_state_current_map = changing_map_state_current_map.replace(".", ",")

                    print(f"[INFO] Character is currently on map: ({changing_map_state_current_map}) ... ")

                    # Checking if detected map's data is in database.
                    if not self.check_if_map_present_in_database(changing_map_state_current_map, MapData.amakna_castle_gobballs):
                        print("[ERROR] Fatal error in 'BotState.CHANGING_MAP'!")
                        print(f"[ERROR] Couldn't detect map ({changing_map_state_current_map}) in database!")
                        print("[ERROR] Exiting ... ")
                        os._exit(1)

                    self.changing_map_state_current_map_detected_successfully = True

                # Uses 'changing_map_state_current_map' to unlock the map data and finds possible directions for the character to move to.
                if self.changing_map_state_current_map_detected_successfully:

                    # List of valid directions for moving.
                    changing_map_state_valid_directions_list = ["top", "bottom", "left", "right"]
                    # Stores possible moving directions from MapData (depends on map).
                    changing_map_state_move_directions_list = []  
                    changing_map_state_current_map_data_list_position = None

                    # Will exit out of program if script fails to change maps too many times.
                    if self.changing_map_state_change_map_attempts_total >= self.changing_map_state_change_map_attempts_allowed:
                        print("[ERROR] Too many failed attemps to change map!")
                        print("[ERROR] Exiting ... ")
                        os._exit(1)   

                    # Getting a list of possible directions to move.
                    for list_index, value in enumerate(MapData.amakna_castle_gobballs):

                        for i_key, i_value in value.items():

                            if changing_map_state_current_map == i_key:

                                for j_key, j_value in i_value.items():

                                    if j_value is not None and j_key in changing_map_state_valid_directions_list:

                                        changing_map_state_move_directions_list.append(j_key)
                                        changing_map_state_current_map_data_list_position = list_index

                    # Generating a random choice from possible choices in 'changing_map_state_move_directions_list'.
                    changing_map_state_move_directions_choice = random.choice(changing_map_state_move_directions_list)

                    # Using the random choice to unlock (x, y) coordinates from map data.
                    changing_map_state_move_directions_x_coordinate = MapData.amakna_castle_gobballs[changing_map_state_current_map_data_list_position][changing_map_state_current_map][changing_map_state_move_directions_choice][0]
                    changing_map_state_move_directions_y_coordinate = MapData.amakna_castle_gobballs[changing_map_state_current_map_data_list_position][changing_map_state_current_map][changing_map_state_move_directions_choice][1]

                    # Clicking on the coordinates to change maps.
                    print(f"[INFO] Clicking on: {(changing_map_state_move_directions_x_coordinate, changing_map_state_move_directions_y_coordinate)} to move '{changing_map_state_move_directions_choice}' ... ")
                    pyautogui.keyDown('e')
                    pyautogui.moveTo(changing_map_state_move_directions_x_coordinate, changing_map_state_move_directions_y_coordinate)
                    # Must wait because 'Dofus' GUI blocks a click when trying to move in 'bottom' direction.
                    time.sleep(self.WAIT_TIME_CHANGING_MAP_CLICK)
                    pyautogui.click()
                    pyautogui.keyUp('e')

                    # Detects if characte changed maps successfully.
                    changing_map_state_click_action_timestamp = time.time()
                    while True:

                        changing_map_state_screenshot_for_map_change_confirmation = self.window_capture.map_detection_capture()
                        changing_map_state_future_map_rectangles_and_text, _, _ = self.detection.ocr_detect_text_from_image(changing_map_state_screenshot_for_map_change_confirmation)

                        # If 'changing_map_state_future_map_rectangles_and_text' is not empty, assign coordinates.
                        if changing_map_state_future_map_rectangles_and_text:
                            changing_map_state_future_map = changing_map_state_future_map_rectangles_and_text[0][1]
                            # Replacing dots with commas in case a dot is detected instead of a comma.
                            changing_map_state_future_map = changing_map_state_future_map.replace(".", ",")
                        else:
                            changing_map_state_future_map = None
                        
                        if changing_map_state_current_map != changing_map_state_future_map and changing_map_state_future_map is not None:
                            #print(f"[INFO] Waiting {self.WAIT_TIME_MAP_LOADING} second(s) for map to load ... ")
                            time.sleep(self.WAIT_TIME_MAP_LOADING)
                            print("[INFO] Map changed successfully!")
                            print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ... ")
                            self.state = BotState.SEARCHING
                            self.changing_map_state_change_map_attempts_total = 0
                            self.changing_map_state_current_map_detected_successfully = False
                            break

                        elif time.time() - changing_map_state_click_action_timestamp > self.WAIT_TIME_BEFORE_TRY_CHANGE_MAP_AGAIN:
                            print("[INFO] Couldn't change map!")
                            print("[INFO] Retrying ... ")
                            self.changing_map_state_change_map_attempts_total += 1
                            break

            
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------THREADING METHODS----------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#


    def DofusBot_Thread_start(self):

        self.DofusBot_Thread_stopped = False
        self.DofusBot_Thread_thread = threading.Thread(target=self.DofusBot_Thread_run)
        self.DofusBot_Thread_thread.start()
        self.threading_tools.wait_for_thread_to_start(self.DofusBot_Thread_thread)


    def DofusBot_Thread_stop(self):

        self.stopped = True
        self.window_capture.Window_Capture_Thread_stop()
        self.Window_VisualDebugOutput_Thread_stop()
        self.threading_tools.wait_for_thread_to_stop(self.DofusBot_Thread_thread)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#


    def Window_VisualDebugOutput_Thread_start(self):

        self.Window_VisualDebugOutput_stopped = False
        self.Window_VisualDebugOutput_Thread_thread = threading.Thread(target=self.Window_VisualDebugOutput_Thread_run)
        self.Window_VisualDebugOutput_Thread_thread.start()
        self.threading_tools.wait_for_thread_to_start(self.Window_VisualDebugOutput_Thread_thread)


    def Window_VisualDebugOutput_Thread_stop(self):

        self.Window_VisualDebugOutput_stopped = True
        self.threading_tools.wait_for_thread_to_stop(self.Window_VisualDebugOutput_Thread_thread)
        

    def Window_VisualDebugOutput_Thread_run(self):

        
        while not self.Window_VisualDebugOutput_stopped:

            loop_time = time.time()

            # Making sure 'window_capture.screenshot_for_VisualDebugOutput_Thread' is not 'None'. Will throw an exception if 'None' & no checking condition.
            # (-215:Assertion failed) size.width>0 && size.height>0 in function 'cv::imshow'.
            if self.window_capture.screenshot_for_VisualDebugOutput_Thread is None:
                continue

            # Draw boxes (rectangles) around detected monsters.
            output_image = self.detection.draw_rectangles(self.window_capture.screenshot_for_VisualDebugOutput_Thread, self.detected_object_rectangles)

            # Displaying the processed image.
            cv.imshow("Matches", output_image)

            # Press 'q' while the DEBUG window is focused to exit.
            if cv.waitKey(1) == ord("q"):
                # Hard exiting and force killing all threads (not clean)
                cv.destroyAllWindows()
                print("Done")
                os._exit(1)

            # Uncomment to display FPS in terminal (WARNING: spams terminal).
            #print(f"FPS {round(1 / (time.time() - loop_time), 2)}")
            loop_time = time.time()


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
