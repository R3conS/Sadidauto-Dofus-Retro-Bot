import cv2 as cv
import numpy as np
import pyautogui
import threading
from threading_tools import Threading_Tools


class Window_Capture:


    # Constants
    GAMEWINDOW_DEFAULT_REGION = (0, 30, 935, 725)


    # Threading Properties
    Window_Capture_Thread_stopped = True
    Window_Capture_Thread_lock = None
    Window_Capture_Thread_thread = None


    # Properties
    screenshot = None
    

    def __init__(self):

        # Initializing a 'threading.Lock()' object.
        self.Window_Capture_Thread_lock = threading.Lock()

        # Initializing a 'Threading_Tools()' object.
        self.threading_tools = Threading_Tools()


    # Screenshoting specified region of the screen. The default is whole game window. 
    # Converting screenshot into required format and returning it.
    def gamewindow_capture(self, capture_region=GAMEWINDOW_DEFAULT_REGION):

        # Region set for (950, 765) size Dofus Window (w, h). The CONSTANT is adjusted with an offset.
        screenshot = pyautogui.screenshot(region=capture_region)
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

        return screenshot


    # Threading Methods.
    def Window_Capture_Thread_start(self):

        self.Window_Capture_Thread_stopped = False
        self.Window_Capture_Thread_thread = threading.Thread(target=self.Window_Capture_Thread_run)
        self.Window_Capture_Thread_thread.start()
        self.threading_tools.wait_for_thread_to_start(self.Window_Capture_Thread_thread)


    def Window_Capture_Thread_stop(self):

        self.Window_Capture_Thread_stopped = True
        self.threading_tools.wait_for_thread_to_stop(self.Window_Capture_Thread_thread)

    
    def Window_Capture_Thread_run(self):

        while not self.Window_Capture_Thread_stopped:

            # Getting an updated image (screenshot) of the game.
            screenshot = self.gamewindow_capture()

            # Locking the thread while updating the results.
            self.Window_Capture_Thread_lock.acquire()
            self.screenshot = screenshot
            self.Window_Capture_Thread_lock.release()
