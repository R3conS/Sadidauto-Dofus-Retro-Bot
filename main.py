import cv2 as cv
import numpy as np
from time import time, sleep
from detection import Detection, Object_Detection
from gamewindow import GameWindow
from window_capture import WindowCapture
from bot import DofusBot, BotState
import threading

# Paths
gobbal_all_images_path = "monster_images\\gobbal_all_images\\"

# Image Lists
gobbal_all_images = [
                    "Gobbal_BL_1.jpg", "Gobbal_BR_1.jpg", "Gobbal_TL_1.jpg", "Gobbal_TR_1.jpg",
                    "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg", "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
                    "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg", "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
                    ]

# Global Variables
DEBUG = True

# OBJECTS
# Initializing 'detection' object
detection = Detection(None)
# Initializing 'window_capture' object
window_capture = WindowCapture()
# Initializing 'monster_detection' object
# monster_detection = Object_Detection(None, gobbal_all_images, gobbal_all_images_path)
# Initializing 'bot' object
dofus_bot = DofusBot(gobbal_all_images, gobbal_all_images_path)

def main():

    # Initializing the WindowCapture class.
    gamewindow = GameWindow("Novella", "v1.35.1")

    if gamewindow.gamewindow_checkifexists() == True:
        gamewindow.gamewindow_resize()

    # THREADS
    # Starting the 'window_capture' thread to start screenshotting the game window.
    window_capture.start()
    # Starting the 'bot' thread.
    dofus_bot.start()

    loop_time = time()
    while True:

        # If no screenshot provided start the loop again.
        if window_capture.screenshot is None:
            continue

        # 'BotState' manager
        if dofus_bot.state == BotState.SEARCHING:
            # Updating 'monster_detection' object inside 'dofus_bot' with an new screenshot image of the game to search for objects in.
            dofus_bot.monster_detection.update(window_capture.screenshot)
            #print("[INFO] 'DofusBot' is in 'SEARCHING' state.")
        elif dofus_bot.state == BotState.COMBAT:
            print("[INFO] 'DofusBot' is in 'COMBAT' state.")

        # print(threading.active_count())
        # print(threading.enumerate())

        if DEBUG:

            # Draw the rectangles around found objects (needle_imgs).
            output_image = detection.draw_rectangles(window_capture.screenshot, dofus_bot.monster_detection.rectangles)
            
            # Displaying the processed image.
            cv.imshow("Matches", output_image)

        # Press 'q' while the DEBUG window is focused to exit.
        if cv.waitKey(1) == ord("q"):
            # Killing created threads after exiting program
            dofus_bot.stop()
            window_capture.stop()
            cv.destroyAllWindows()
            print("Done")
            break

        #print(f"FPS {round(1 / (time() - loop_time), 2)}")
        loop_time = time()

if __name__ == '__main__':
    main()

