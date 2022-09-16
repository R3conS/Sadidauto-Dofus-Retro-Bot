import cv2 as cv
import numpy as np
import pyautogui
import threading
from threading_tools import Threading_Tools


class Window_Capture:


    # Constants.
    # The region of the screen where screenshots for 'haystack' images are made. This value should NEVER be touched.
    # The width and height values aren't the same as the 'Dofus.exe' window itself, because 'pyautogui.screenshot()' captures a little more than needed.
    # The (x, y, w, h) values are adjusted to have no black bars & no Windows top bar.
    GAMEWINDOW_DEFAULT_REGION = (0, 30, 933, 725)
    # Region to screenshot for map detection.
    MAP_DETECTION_CAPTURE_REGION = (522, 650, 48, 30)
    #MAP_DETECTION_CAPTURE_REGION = (515, 645, 70, 45)


    # Threading Properties
    Window_Capture_Thread_stopped = True
    Window_Capture_Thread_lock = None
    Window_Capture_Thread_thread = None


    # Properties
    screenshot_for_object_detection = None
    screenshot_for_VisualDebugOutput_Thread = None
    

    def __init__(self):

        # Initializing a 'threading.Lock()' object.
        self.Window_Capture_Thread_lock = threading.Lock()

        # Initializing a 'Threading_Tools()' object.
        self.threading_tools = Threading_Tools()


    # Screenshoting specified region of the screen. The default is whole game window. 
    # Converting screenshot into required format and returning it.
    def gamewindow_capture(self, capture_region=GAMEWINDOW_DEFAULT_REGION):

        # Region set for (950, 765) size Dofus Window (w, h). The CONSTANT is adjusted with an offset.
        screenshot_for_object_detection = pyautogui.screenshot(region=capture_region)
        screenshot_for_object_detection = np.array(screenshot_for_object_detection)
        screenshot_for_object_detection = cv.cvtColor(screenshot_for_object_detection, cv.COLOR_RGB2BGR)

        screenshot_for_VisualDebugOutput_Thread = pyautogui.screenshot(region=capture_region)
        screenshot_for_VisualDebugOutput_Thread = np.array(screenshot_for_VisualDebugOutput_Thread)
        screenshot_for_VisualDebugOutput_Thread = cv.cvtColor(screenshot_for_VisualDebugOutput_Thread, cv.COLOR_RGB2BGR)

        return screenshot_for_object_detection, screenshot_for_VisualDebugOutput_Thread

    
    # Screenshoots the minimap area.
    def map_detection_capture(self, capture_region=MAP_DETECTION_CAPTURE_REGION):

        # Moving mouse over the red area on the minimap for the black map tooltip to appear.
        pyautogui.moveTo(517, 680)

        # Getting a screenshot.
        screenshot_for_map_detection = pyautogui.screenshot(region=capture_region)
        screenshot_for_map_detection = np.array(screenshot_for_map_detection)
        screenshot_for_map_detection = cv.cvtColor(screenshot_for_map_detection, cv.COLOR_RGB2GRAY)

        # Upscaling the screenshot.
        PERCENTAGE_WIDTH = 215
        PERCENTAGE_HEIGHT = 200
        width = int(screenshot_for_map_detection.shape[1] * PERCENTAGE_WIDTH / 100)
        height = int(screenshot_for_map_detection.shape[0] * PERCENTAGE_HEIGHT / 100)
        dimensions = (width, height)
        screenshot_for_map_detection = cv.resize(screenshot_for_map_detection, dimensions, interpolation=cv.INTER_AREA)

        # Moving mouse off the red area on the minimap in case a new screenshot is required for another detection.
        pyautogui.move(20, 0)

        return screenshot_for_map_detection


    # Takes a screenshot around mouse. 
    # 'rect_size' - controls how big the screenshot (rectangle around mouse) will be.
    def area_around_mouse_capture(self, rect_size):

        mouse_pos = pyautogui.position()

        center_x = mouse_pos[0]
        center_y = mouse_pos[1]

        topleft_x = center_x - rect_size
        topleft_y = center_y - rect_size

        bottomright_x = center_x + rect_size
        bottomright_y = center_y + rect_size

        width = bottomright_x - topleft_x
        height = bottomright_y - topleft_y

        capture_region = (topleft_x, topleft_y, width, height)

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
            screenshot_for_object_detection, screenshot_for_VisualDebugOutput_Thread = self.gamewindow_capture()

            # Locking the thread while updating the results.
            self.Window_Capture_Thread_lock.acquire()
            self.screenshot_for_object_detection = screenshot_for_object_detection
            self.screenshot_for_VisualDebugOutput_Thread = screenshot_for_VisualDebugOutput_Thread
            self.Window_Capture_Thread_lock.release()
