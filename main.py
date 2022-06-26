import cv2 as cv
import numpy as np
from time import time, sleep
from detection import Detection, Object_Detection
from gamewindow import GameWindow
from char_status import CharStatus
import pyautogui
import threading

# Paths
gobbal_images_path = "monster_images\\gobbal_images\\"
gobbly_black_images_path = "monster_images\\gobbly_black_images\\"
gobbly_white_images_path = "monster_images\\gobbly_white_images\\"

# Image Lists
gobbal_images = ["Gobbal_BL_1.jpg", "Gobbal_BR_1.jpg", "Gobbal_TL_1.jpg", "Gobbal_TR_1.jpg"]
gobbly_black_images = ["GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg", "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg"]
gobbly_white_images = ["GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg", "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg"]

# Global Variables
DEBUG = True

# Initializing detection object
detection = Detection(None)

is_bot_in_action = False


def bot_actions(gobbal_rectangles, gobbal_center_xy_coordinates):

    if len(gobbal_rectangles) > 0:
            targets = gobbal_center_xy_coordinates
            target = detection.get_offset_click_points(targets[0])
            pyautogui.moveTo(x=target[0], y=target[1])
            pyautogui.click()
            sleep(5)
    
    global is_bot_in_action
    is_bot_in_action = False



def main():

    # Initializing the WindowCapture class
    gamewindow = GameWindow("Novella", "v1.35.1")

    if gamewindow.gamewindow_checkifexists() == True:
        gamewindow.gamewindow_resize()


    monster_detection = Object_Detection(None, gobbal_images, gobbal_images_path)


    # Starting the gamewindow_capture thread to get an updated screenshot of the game
    detection.start()

    # Starting the monster detection thread
    monster_detection.start()


    loop_time = time()
    while True:

        global is_bot_in_action

        if detection.screenshot is None:
            continue

        # Give monster_detection object an updated screenshot image of the game to search for objects in
        monster_detection.update(detection.screenshot)

        if DEBUG:
            # Draw the rectangles around found objects (needle_imgs)
            output_image = detection.draw_rectangles(detection.screenshot, monster_detection.rectangles)
            # Displaying the processed image
            cv.imshow("Matches", output_image)

            if cv.waitKey(1) == ord("q"):
                # Killing created threads after exiting program
                monster_detection.stop()
                detection.stop()
                cv.destroyAllWindows()
                print("Done")
                break


        # Take Bot actions
        if not is_bot_in_action:

            is_bot_in_action = True
            t = threading.Thread(target=bot_actions, args=(monster_detection.rectangles, monster_detection.click_points))
            t.start()

        
        print(f"FPS {round(1 / (time() - loop_time), 2)}")
        loop_time = time()

        
        
if __name__ == '__main__':
    main()

