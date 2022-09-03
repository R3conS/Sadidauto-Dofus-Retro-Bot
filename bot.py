import threading
import pyautogui
from detection import Detection, Object_Detection
import time
import os

class ImageData:


    bot_state_images_path = "status_images\\bot_state_images\\"
    bot_state_incombat = "combat_incombat.jpg"
    
    gobbal_all_images_path = "monster_images\\gobbal_all_images\\"
    gobbal_all_images = [
                    "Gobbal_BL_1.jpg", "Gobbal_BR_1.jpg", "Gobbal_TL_1.jpg", "Gobbal_TR_1.jpg",
                    "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg", "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
                    "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg", "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
                        ]


class BotState:


    INITIALIZING = "INITIALIZING"
    SEARCHING = "SEARCHING"
    ATTACKING = "ATTACKING"
    COMBAT = "COMBAT"
    CHANGING_MAP = "CHANGING_MAP"


class DofusBot:


    # Constants.
    WAIT_TIME_INITIALIZING = 5
    WAIT_TIME_SCRIPT_ACTIONS = 0.5
    WAIT_TIME_BOTSTATE_SEARCHING = 0.75


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

        # Initializing 'monster_detection' object. Handles detecting monsters on the screen.
        self.monster_detection = Object_Detection(None, self.monster_images_to_detect, self.monster_images_to_detect_path)


    def check_current_BotState(self):
        
        return self.state


    def start(self):

        self.stopped = False
        t = threading.Thread(target=self.DofusBot_Thread)
        t.start()


    def stop(self):

        self.stopped = True
        self.monster_detection.stop()

    
    def DofusBot_Thread(self):

        print("[INFO] 'Bot' thread started!")

        while not self.stopped:

            # The bot always starts up in this (INITIALIZING) state. 
            # From here, it starts the 'monster_detection' thread and changes it's state to SEARCHING.
            if self.state == BotState.INITIALIZING:

                print(f"[INFO] 'DofusBot' is currently in 'BotState': {self.check_current_BotState()}.")

                for i in range(self.WAIT_TIME_INITIALIZING, -1, -1):

                    if i == 0:

                        print(f"[INFO] Changing 'BotState' to: '{BotState.SEARCHING}'...")
                        self.state = BotState.SEARCHING
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        print(f"[INFO] 'DofusBot' is currently in 'BotState': {self.check_current_BotState()}.")
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        print(f"[INFO] Starting 'ObjectDetection_Thread' in 'monster_detection' object...")
                        self.monster_detection.start()
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                        try:
                            if self.monster_detection.threadas.is_alive():
                                print(f"[INFO] {self.monster_detection.threadas.getName()} started succesfully!")
                        except AttributeError:
                            print("[ERROR] Couldn't start 'ObjectDetection_Thread' in 'monster_detection' object!")
                            print("[ERROR] Exiting...")
                            os._exit(1)

                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

                    else:
                        print(f"[INFO] Changing 'BotState' to '{BotState.SEARCHING}' and starting 'monster_detection' thread in: {i}...")
                        time.sleep(self.WAIT_TIME_SCRIPT_ACTIONS)

            elif self.state == BotState.SEARCHING:

                if len(self.monster_detection.click_points) > 1:
                    print(f"[INFO] Monsters found at: {self.monster_detection.click_points}")
                    time.sleep(self.WAIT_TIME_BOTSTATE_SEARCHING)
                else:
                    print("[INFO] Couldn't find any monsters... changing map.")
                    time.sleep(self.WAIT_TIME_BOTSTATE_SEARCHING)





