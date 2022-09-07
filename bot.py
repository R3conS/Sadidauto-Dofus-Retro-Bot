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
    # Time to wait inbetween various script actions/steps. 
    WAIT_TIME_SCRIPT_ACTIONS = 0
    WAIT_TIME_INITIALIZE_Window_Capture_Thread = 1


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
    detection_threshold = None
    

    # Used in 'detect_objects()'.
    detected_object_rectangles = []
    detected_object_click_points = []

    
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
            # Starts 'Window_Capture_Thread', if needed starts the 'Window_VisualDebugOutput_Thread' and changes it's state to 'SEARCHING'.
            if self.state == BotState.INITIALIZING:

                print(f"[INFO] 'DofusBot' is currently in 'BotState': {self.check_BotState_current()}!")

                # Starting the 'Window_Capture_Thread' thread to start screenshotting the game window. 
                self.window_capture.Window_Capture_Thread_start()
                time.sleep(self.WAIT_TIME_INITIALIZE_Window_Capture_Thread)

                # Launches an 'OpenCV' window for debug purposes.
                if self.Window_VisualDebugOutput_window:
                    # Starting' Window_VisualDebugOutput_Thread'.
                    self.Window_VisualDebugOutput_Thread_start()

                print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}' ...")
                self.state = BotState.SEARCHING
                self.check_BotState_change_success_OR_fail("SEARCHING")

            # This state handles the monster detection.
            # If monsters are detected, the 'BotState' changes to 'ATTACKING'.
            # If nothing is detected, the 'BotState' changes to 'CHANGING_MAP'.
            elif self.state == BotState.SEARCHING:
                    
                    self.detected_object_rectangles, self.detected_object_click_points = self.detection.detect_objects(
                                                                                                                        self.objects_to_detect_list, 
                                                                                                                        self.objects_to_detect_path, 
                                                                                                                        self.window_capture.screenshot_for_object_detection,
                                                                                                                        threshold=self.detection_threshold,
                                                                                                                        )

                    # EXECUTE THIS BLOCK IF MONSTERS WERE DETECTED
                    if len(self.detected_object_click_points) > 0:

                        print(f"[INFO] Monsters found at: {self.detected_object_click_points}")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.ATTACKING}' ...")
                        self.state = BotState.ATTACKING
                        self.check_BotState_change_success_OR_fail("ATTACKING")
                            
                    # EXECUTE THIS BLOCK IF MONSTERS WERE **NOT** DETECTED
                    elif len(self.detected_object_click_points) <= 0:

                        print(f"[INFO] Couldn't find any monsters ... ")
                        print(f"[INFO] Changing 'BotState' to: '{BotState.CHANGING_MAP}' ... ")
                        self.state = BotState.CHANGING_MAP
                        self.check_BotState_change_success_OR_fail("CHANGING_MAP")

            # Handles attacking found monsters by 'SEARCHING' state
            elif self.state == BotState.ATTACKING:               
                print("[INFO] Attacking")
                time.sleep(1)

            # Handles map changing when bot doesn't detect any monsterss
            elif self.state == BotState.CHANGING_MAP:
                print("[INFO] Changing map")
                time.sleep(1)


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
