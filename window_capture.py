import cv2 as cv
import numpy as np
import pyautogui
import threading


class WindowCapture:


    # Constants
    GAMEWINDOW_DEFAULT_REGION = (0, 30, 935, 725)


    # Threading Properties
    stopped = True
    lock = None
    threadas = None


    # Properties
    screenshot = None
    

    def __init__(self):

        # Creating a thread lock object
        self.lock = threading.Lock()


    # Screenshoting specified region of the screen. The default is whole game window. 
    # Converting screenshot into required format and returning it.
    def gamewindow_capture(self, capture_region=GAMEWINDOW_DEFAULT_REGION):

        screenshot = pyautogui.screenshot(region=capture_region) # Region set for (950, 765) size Dofus Window (w, h)
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

        return screenshot


    # Threading Methods
    def start(self):

        self.stopped = False
        self.threadas = threading.Thread(target=self.WindowCapture_Thread)
        self.threadas.start()


    def stop(self):

        self.stopped = True

    
    def WindowCapture_Thread(self):

        while not self.stopped:

            # Get an updated image of the game
            screenshot = self.gamewindow_capture()

            # Lock the thread while updating the results
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()

