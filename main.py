import cv2 as cv
import time
from detection import Detection
from gamewindow import GameWindow
from bot import DofusBot, ImageData

# Global Variables
DEBUG = True

# Initializing 'detection' object
detection = Detection()
# Initializing 'bot' object
dofus_bot = DofusBot(ImageData.gobbal_images_list, ImageData.gobbal_images_path)
#dofus_bot = DofusBot(ImageData.test_monster_images_list, ImageData.test_monster_images_path)

def main():

    # Initializing the WindowCapture class.
    gamewindow = GameWindow("Novella", "v1.35.1")

    if gamewindow.gamewindow_checkifexists() == True:
        gamewindow.gamewindow_resize()

    # Starting the 'bot' thread.
    dofus_bot.start()

    loop_time = time.time()
    while True:

        #If no screenshot provided start the loop again.
        if dofus_bot.window_capture.screenshot is None:
            continue

        if DEBUG:

            # Draw the rectangles around found objects (needle_imgs).
            output_image = detection.draw_rectangles(dofus_bot.window_capture.screenshot, dofus_bot.monster_detection.rectangles)
            
            # Displaying the processed image.
            cv.imshow("Matches", output_image)

        # Press 'q' while the DEBUG window is focused to exit.
        if cv.waitKey(1) == ord("q"):
            # Killing created threads after exiting program
            dofus_bot.stop()
            cv.destroyAllWindows()
            print("Done")
            break

        #print(f"FPS {round(1 / (time.time() - loop_time), 2)}")
        loop_time = time.time()

if __name__ == '__main__':
    main()

