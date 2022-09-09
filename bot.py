import threading
import pyautogui
import time
import os
import cv2 as cv
from detection import Detection
from window_capture import Window_Capture
from threading_tools import Threading_Tools


class ImageData:
    

    test_monster_images_path = "test_monster_images\\"
    test_monster_images_list = ["test_1.jpg", "test_2.jpg", "test_3.jpg", "test_4.jpg"]

    gobball_images_path = "monster_images\\gobball_all_images\\"
    gobball_images_list = [
                         "Gobball_BL_1.jpg", "Gobball_BR_1.jpg", "Gobball_TL_1.jpg", "Gobball_TR_1.jpg",
                         "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg", "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
                         "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg", "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
                         ]


class MapData:


    amakna_castle_gobballs = [

        {"3,-9": {"top": (  None  ), "bottom": (500, 580), "left": (  None  ), "right": (900, 310)} },
        {"4,-9": {"top": (  None  ), "bottom": (500, 580), "left": (30 , 310), "right": (900, 275)} },
        {"5,-9": {"top": (  None  ), "bottom": (435, 580), "left": (30 , 270), "right": (  None  )} },
        {"3,-8": {"top": (500 , 70), "bottom": (  None  ), "left": (  None  ), "right": (900, 310)} },
        {"4,-8": {"top": (500 , 70), "bottom": (  None  ), "left": (30 , 275), "right": (900, 310)} },
        {"5,-8": {"top": (430 , 70), "bottom": (  None  ), "left": (30 , 310), "right": (  None  )} },

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
    WAIT_TIME_AFTER_ATTACKING_MONSTER = 7
    # Time to wait after clicking ready in 'BotState.PREPARATION'. Determines how long script will keep chacking if combat was started successfully.
    WAIT_TIME_COMBAT_START = 10
    # Time to wait before checking again if the 'Fight Results' window was properly closed in 'BotState.IN_COMBAT'.
    WAIT_TIME_FIGHT_RESULT_WINDOW_CLOSED = 3


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

                        print(f"[INFO] Monsters found at: '{self.detected_object_click_points}'!")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.ATTACKING}' ...")
                        self.state = BotState.ATTACKING
                            
                    # EXECUTE THIS BLOCK IF MONSTERS WERE **NOT** DETECTED.
                    elif len(self.detected_object_click_points) <= 0:

                        print("[INFO] Couldn't find any monsters ... ")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.CHANGING_MAP}' ... ")
                        self.state = BotState.CHANGING_MAP


            # Handles attacking found monsters by 'SEARCHING' state.
            elif self.state == BotState.ATTACKING:

                attacking_state_attack_successful = False
                attacking_state_attack_attempts = 0

                # Keep trying all coordinates in 'detected_object_click_points' list until combat starts.
                if attacking_state_attack_attempts < len(self.detected_object_click_points):

                    for click_points in self.detected_object_click_points:

                        x_coordinate, y_coordinate = click_points

                        # Separating moving mouse and clicking into two actions instead of one, because otherwise it sometimes right clicks too early,
                        # causing the character to fail an attack.
                        print(f"[INFO] Attacking monster at: {click_points} ... ")
                        pyautogui.moveTo(x=x_coordinate, y=y_coordinate, duration=self.move_duration)
                        pyautogui.click(button="right")
                        attacking_state_attack_attempts += 1

                        # This loop will keep trying to find 'status_images' that confirm if the monster was attacked succesfully.
                        # The wait time is controlled by 'WAIT_TIME_AFTER_ATTACKING_MONSTER'.
                        # If images were detected, then combat was started successfully and the bot will change state to 'PREPARATION'.
                        # If images are not detected within the time specified, the 'while' loop will break to start the next 'for' loop iteration
                        # and try the next coordinates.
                        attack_action_start_time = time.time()
                        while True:

                            cc_icon_attacking_state = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\PREPARATION_state_verifier_1.jpg")
                            ready_button_attacking_state = self.detection.find(self.window_capture.screenshot_for_object_detection, "status_images\\PREPARATION_state_verifier_2.jpg")
                            
                            if time.time() - attack_action_start_time > self.WAIT_TIME_AFTER_ATTACKING_MONSTER:
                                print(f"[INFO] Failed to attack monster at: '{click_points}' ... ")
                                print(f"[INFO] Trying the next coordinates ... ")
                                break

                            elif len(cc_icon_attacking_state) > 0 and len(ready_button_attacking_state) > 0:
                                print(f"[INFO] Successfully attacked monster at: {click_points} !")
                                print(f"[INFO] Changing 'BotState' to: '{BotState.PREPARATION}' ... ")
                                self.state = BotState.PREPARATION
                                attacking_state_attack_successful = True
                                break

                        if attacking_state_attack_successful:
                            break

                # If all coordinates in 'detected_object_click_points' have been tried and combat hasn't started, change state to 'SEARCHING'
                # to get a new coordinate list.
                if attacking_state_attack_attempts == len(self.detected_object_click_points):

                    print("[INFO] Tried all coordinates within found monsters list!")
                    print("[INFO] Failed to start combat!")
                    print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ... ")
                    self.state = BotState.SEARCHING


            # Handles selecting best starting position and starting combat.
            elif self.state == BotState.PREPARATION:

                # Resetting both values to empty lists, so the 'output_image' in 'Window_VisualDebugOutput_Thread_run()' is clean.
                # This will prevent script from drawing rectangles around, or markers on, found objects.
                self.detected_object_rectangles = []
                self.detected_object_click_points = []

                print("[INFO] Clicking on best starting position ... ")

                #------------------------------------------------------
                # TO BE CREATED: Finding out best cell to start on.
                #------------------------------------------------------

                # Checking if combat has ended.
                preparation_state_ready_button_click_action = False
                while True:

                    preparation_state_ready_button_icon = self.detection.get_click_points(self.detection.find(self.window_capture.screenshot_for_object_detection, 
                                                                                      "status_images\\PREPARATION_state_verifier_2.jpg"))

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
                            print("[INFO] Failed to start combat, retrying ... ")
                            preparation_state_ready_button_click_action = False

                        elif len(preparation_state_cc_icon) > 0 and len(preparation_state_ap_icon) > 0 and len(preparation_state_mp_icon) > 0:
                            print("[INFO] Successfully started combat!")
                            print(f"[INFO] Changing 'BotState' to: '{BotState.IN_COMBAT}' ... ")
                            self.state = BotState.IN_COMBAT
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
                            print("[INFO] Failed to close 'Fight Results' window ... ")
                            print("[INFO] Retrying ... ")
                            in_combat_state_close_button_click_action = False
                        
                        elif len(in_combat_state_close_button_icon) <= 0 and len(in_combat_state_cc_icon) <= 0:
                            print("[INFO] Successfully closed 'Fight Results' window!")
                            print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ... ")
                            self.state = BotState.SEARCHING
                            break

                        
            # Handles map changing when bot doesn't detect any monsters.
            elif self.state == BotState.CHANGING_MAP:

                print("[INFO] Changing map")

                #------------------------------------------------------
                # TO BE CREATED: Map changing logic
                #------------------------------------------------------

                # For debug purposes.
                self.state = BotState.SEARCHING
                time.sleep(3)

            
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
