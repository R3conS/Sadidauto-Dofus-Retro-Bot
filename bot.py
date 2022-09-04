import threading
import pyautogui
from detection import Detection, Object_Detection
from window_capture import WindowCapture
import time
import os


class ImageData:
    

    test_monster_images_path = "test_monster_images\\"
    test_monster_images_list = ["test_1.jpg", "test_2.jpg", "test_3.jpg", "test_4.jpg"]

    gobbal_images_path = "monster_images\\gobbal_all_images\\"
    gobbal_images_list = [
                         "Gobbal_BL_1.jpg", "Gobbal_BR_1.jpg", "Gobbal_TL_1.jpg", "Gobbal_TR_1.jpg",
                         "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg", "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
                         "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg", "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
                         ]


class BotState:


    INITIALIZING = "INITIALIZING"
    SEARCHING = "SEARCHING"
    ATTACKING = "ATTACKING"
    PREPARATION = "PREPARATION"
    COMBAT = "COMBAT"
    CHANGING_MAP = "CHANGING_MAP"


class DofusBot:


    # Constants.
    # Time to wait before changing to 'SEARCHING' state during 'INITIALIZING' state.
    WAIT_TIME_INITIALIZING = 3
    # Time to wait inbetween various script actions/steps.
    WAIT_TIME_SCRIPT_ACTIONS = 0.25
    # Time to wait before searching for new objects in 'SEARCHING' state. 
    WAIT_TIME_BOTSTATE_SEARCHING = 1
    

    # Threading Properties.
    stopped = True
    lock = None


    # Properties.
    monster_images_to_detect = None
    monster_images_to_detect_path = None

    
    def __init__(self, monster_images_to_detect, monster_images_to_detect_path):

        self.monster_images_to_detect = monster_images_to_detect
        self.monster_images_to_detect_path = monster_images_to_detect_path

        # Default state of the bot at the start
        self.state = BotState.INITIALIZING

        # Initializing thread lock object
        self.lock = threading.Lock()

        # Initializing 'window_capture' object. Handles screenshotting the game window.
        self.window_capture = WindowCapture()

        # Initializing 'monster_detection' object. Handles detecting monsters on the screen.
        self.monster_detection = Object_Detection(self.monster_images_to_detect, self.monster_images_to_detect_path)

 
    def check_BotState_current(self):

        return self.state

    
    def check_BotState_change_success_OR_fail(self, change_state_to):
    
        if self.check_BotState_current() == change_state_to:
            print(f"[INFO] 'DofusBot' successfully changed 'BotState' to: {self.check_BotState_current()}!")
        else:
            print(f"[ERROR] Failed to change 'BotState' from '{self.check_BotState_current()}' to '{change_state_to}'")
            print(f"[ERROR] Exiting ...")
            os._exit(1)


    def check_thread_alive_OR_dead(self, thread_name):

        if thread_name.is_alive():
            print(f"[INFO] {thread_name} is 'ALIVE'!")
            return "ALIVE"
        elif not thread_name.is_alive():
            print(f"[INFO] {thread_name} is 'DEAD'!")
            return "DEAD"


    def start(self):

        self.stopped = False
        t = threading.Thread(target=self.DofusBot_Thread)
        t.start()


    def stop(self):

        self.stopped = True
        self.monster_detection.stop()
        self.window_capture.stop()

    
    def DofusBot_Thread(self):

        print("[INFO] 'Bot' thread started!")
    
        while not self.stopped:

            # The bot always starts up in this (INITIALIZING) state. 
            # Starts the 'monster_detection' thread, starts the 'window_capture' thread and changes it's state to 'SEARCHING'.
            if self.state == BotState.INITIALIZING:

                print(f"[INFO] 'DofusBot' is currently in 'BotState': {self.check_BotState_current()}!")

                for i in range(self.WAIT_TIME_INITIALIZING, -1, -1):

                    if i == 0:

                        print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ...")
                        self.state = BotState.SEARCHING
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        # Checking if 'BotState' change was successful.
                        self.check_BotState_change_success_OR_fail("SEARCHING")
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        # Starting the 'WindowCapture_Thread' thread to start screenshotting the game window.
                        print(f"[INFO] Starting 'WindowCapture_Thread' in 'WindowCapture' object ...")
                        self.window_capture.start()

                        # Checking if the thread started successfully. Stop the program if it didn't.
                        if self.check_thread_alive_OR_dead(self.window_capture.threadas) == "Dead":
                            os._exit(1)

                        # Starting the 'ObjectDetection_Thread' to start detecting monsters.
                        print(f"[INFO] Starting 'ObjectDetection_Thread' in 'monster_detection' object ...")                        
                        self.monster_detection.start()

                        # Checking if the thread started successfully. Stop the program if it didn't.
                        if self.check_thread_alive_OR_dead(self.monster_detection.threadas) == "Dead":
                            os._exit(1)

                        # Script will briefly lag at this point and might give a false result until it reaches the "SEARCHING" logic where it gets
                        # an updated screenshot of the game. Works better if instantly given a screenshot to work on.
                        self.monster_detection.update(self.window_capture.screenshot)
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    else:

                        print(f"[INFO] Changing 'BotState' to '{BotState.SEARCHING}' in: {i} ...")
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)


            # This state handles the monster detection. If monsters are detected, the 'BotState' changes to 'ATTACKING' and
            # 'monster_detection' thread is stopped. If nothing is detected, switches to 'CHANGING_MAP' state.
            elif self.state == BotState.SEARCHING:

                # Constantly updating 'monster_detection' with a new screenshot of the game
                self.monster_detection.update(self.window_capture.screenshot)
                
                # Giving time for 'monster_detection' thread to initialize properly. Best to keep at >= 1 seconds.
                print("[INFO] Searching ... ")
                time.sleep(self.WAIT_TIME_BOTSTATE_SEARCHING)

                # EXECUTE THIS BLOCK IF MONSTERS WERE DETECTED
                if len(self.monster_detection.click_points) > 0:

                    print(f"[INFO] Monsters found at: {self.monster_detection.click_points}")
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    print(f"[INFO] Changing 'BotState' to: '{BotState.ATTACKING}' ...")
                    self.state = BotState.ATTACKING
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    # Checking if 'BotState' change was successful.
                    self.check_BotState_change_success_OR_fail("ATTACKING")
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    print(f"[INFO] Stopping 'ObjectDetection_Thread' in 'monster_detection' object (FOUND MONSTERS) ...")
                    self.monster_detection.stop()

                    # Giving time for the thread to stop. Make sure it's >= 1 second.
                    time.sleep(1)

                    # Checking if 'ObjectDetection_Thread' in 'monster_detection' object was stopped successfully.
                    if self.check_thread_alive_OR_dead(self.monster_detection.threadas) == "Alive":
                        os._exit(1)
                        
                elif len(self.monster_detection.click_points) <= 0:

                    print("[INFO] Couldn't find any monsters ...")

                    print(f"[INFO] Changing 'BotState' to: '{BotState.CHANGING_MAP}' ...")
                    self.state = BotState.CHANGING_MAP
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    # Checking if 'BotState' change was successful.
                    self.check_BotState_change_success_OR_fail("CHANGING_MAP")
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    print(f"[INFO] Stopping 'ObjectDetection_Thread' in 'monster_detection' object ... ")
                    self.monster_detection.stop()

                    # Giving time for the thread to stop. Make sure it's >= 1 second.
                    time.sleep(1)

                    # Checking if 'ObjectDetection_Thread' in 'monster_detection' object was stopped successfully.
                    if self.check_thread_alive_OR_dead(self.monster_detection.threadas) == "Alive":
                        os._exit(1)

            # Handles attacking found monsters by 'SEARCHING' state
            elif self.state == BotState.ATTACKING:
                print("[INFO] Attacking")
                time.sleep(1)


            # Handles map changing when bot doesn't detect any monsterss
            elif self.state == BotState.CHANGING_MAP:
                print("[INFO] Changing map")
                time.sleep(1)


