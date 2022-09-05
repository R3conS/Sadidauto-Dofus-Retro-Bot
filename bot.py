import threading
import pyautogui
import time
import os
import cv2 as cv
from detection import Detection, Object_Detection
from window_capture import Window_Capture
from threading_tools import Threading_Tools



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
    WAIT_TIME_SCRIPT_ACTIONS = 0.1
    # Time to wait before starting a new detection cycle in 'SEARCHING' state.
    # The lower the number, the more chance the detection wont work properly on a slower machine (like a VM).
    # Detection seems to work properly on 2GB Ram + 2 core CPU.
    WAIT_TIME_BOTSTATE_SEARCHING = 3
    # Time to wait after a 'thread.stop()' call. Gives time for a thread to properly stop before continuing.
    WAIT_TIME_THREAD_STOP = 2
    

    # 'DofusBot_Thread' threading properties.
    DofusBot_Thread_stopped = True
    DofusBot_Thread_thread = None


    # 'Window_VisualDebugOutput_Thread' threading properties.
    Window_VisualDebugOutput_Thread_stopped = True
    Window_VisualDebugOutput_Thread_thread = None


    # Properties.
    monster_images_to_detect = None
    monster_images_to_detect_path = None
    debug_window = None

    
    def __init__(self, monster_images_to_detect, monster_images_to_detect_path, debug_window=False):

        # Loading monster/object images.
        self.monster_images_to_detect = monster_images_to_detect
        self.monster_images_to_detect_path = monster_images_to_detect_path

        # If 'True', will allow bot to run 'Window_VisualDebugOutput_Thread_start' which opens an 'OpenCV' debug window.
        self.debug_window = debug_window

        # Default state of the bot at the start.
        self.state = BotState.INITIALIZING

        # Initializing 'Threading_Tools()' object. Holds various custom threading methods.
        self.threading_tools = Threading_Tools()

        # Initializing 'Window_Capture()' object. Handles screenshotting the game window.
        self.window_capture = Window_Capture()

        # Initializing 'Object_Detection()' object. Handles detecting monsters on the screen.
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


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------MAIN THREAD OF CONTROL---------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#


    def DofusBot_Thread_run(self):

        while not self.DofusBot_Thread_stopped:

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

                        # Starting the 'Window_Capture_Thread' thread to start screenshotting the game window.
                        self.window_capture.Window_Capture_Thread_start()
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        # Starting the 'Object_Detection_Thread' to start detecting monsters.                   
                        self.monster_detection.Object_Detection_Thread_start()
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        # Launches an 'OpenCV' window for debug purposes.
                        if self.debug_window:
                            # Starting the DEBUG output window thread
                            self.Window_VisualDebugOutput_Thread_start()
                            time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    else:

                        print(f"[INFO] Changing 'BotState' to '{BotState.SEARCHING}' in: {i} ...")
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)


            # This state handles the monster detection. 
            # If monsters are detected, the 'BotState' changes to 'ATTACKING' and 'monster_detection' thread is stopped.
            # If nothing is detected, the 'BotState' changes to 'CHANGING_MAP' and 'monster_detection' thread is stopped.
            elif self.state == BotState.SEARCHING:

                # Constantly updating 'monster_detection' with a new screenshot of the game
                self.monster_detection.update(self.window_capture.screenshot)
                
                # Giving time for 'monster_detection' thread to search for monsters thoroughly.
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

                    # Stopping 'Object_Detection_Thread'.
                    self.monster_detection.Object_Detection_Thread_stop()
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)
                        
                # EXECUTE THIS BLOCK IF MONSTERS WERE **NOT** DETECTED
                elif len(self.monster_detection.click_points) <= 0:

                    print("[INFO] Couldn't find any monsters ...")

                    print(f"[INFO] Changing 'BotState' to: '{BotState.CHANGING_MAP}' ...")
                    self.state = BotState.CHANGING_MAP
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    # Checking if 'BotState' change was successful.
                    self.check_BotState_change_success_OR_fail("CHANGING_MAP")
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    # Stopping 'Object_Detection_Thread'.
                    self.monster_detection.Object_Detection_Thread_stop()
                    time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)


            # Handles attacking found monsters by 'SEARCHING' state
            elif self.state == BotState.ATTACKING:
                print("[INFO] Attacking")
                time.sleep(2.5)

            # Handles map changing when bot doesn't detect any monsterss
            elif self.state == BotState.CHANGING_MAP:
                print("[INFO] Changing map")
                time.sleep(2.5)


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
        self.monster_detection.stop()
        self.window_capture.stop()
        self.threading_tools.wait_for_thread_to_stop(self.DofusBot_Thread_thread)


    def Window_VisualDebugOutput_Thread_start(self):

        self.Window_VisualDebugOutput_stopped = False
        self.Window_VisualDebugOutput_Thread_thread = threading.Thread(target=self.Window_VisualDebugOutput_Thread_run)
        self.Window_VisualDebugOutput_Thread_thread.start()
        self.threading_tools.wait_for_thread_to_start(self.Window_VisualDebugOutput_Thread_thread)


    def Window_VisualDebugOutput_Thread_stop(self):

        self.Window_VisualDebugOutput_stopped = True
        self.threading_tools.wait_for_thread_to_stop(self.Window_VisualDebugOutput_Thread_thread)
        

    def Window_VisualDebugOutput_Thread_run(self):

        loop_time = time.time()
        while not self.Window_VisualDebugOutput_stopped:

            # If no screenshot provided yet, start the loop again.
            if self.window_capture.screenshot is None:
                continue
        
            # Draw boxes (rectangles) around detected monsters.
            output_image = self.monster_detection.draw_rectangles(self.window_capture.screenshot, self.monster_detection.rectangles)
            
            # Displaying the processed image.
            cv.imshow("Matches", output_image)

            # Press 'q' while the DEBUG window is focused to exit.
            if cv.waitKey(1) == ord("q"):
                # Hard exiting and force killing all threads (not clean)
                cv.destroyAllWindows()
                print("Done")
                os._exit(1)

            # Uncomment to display FPS in terminal (spams terminal).
            #print(f"FPS {round(1 / (time.time() - loop_time), 2)}")
            loop_time = time.time()


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
