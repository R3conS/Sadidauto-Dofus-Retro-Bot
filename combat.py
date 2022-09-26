from detection import Detection
from window_capture import Window_Capture


class Combat:


    def __init__(self):
        
        # Initializing 'window_capture' object.
        self.window_capture = Window_Capture()

        # Initializing 'detection' object.
        self.detection = Detection()


    def get_ap(self):
        
        ap_screenshot = self.window_capture.ap_area_capture()
        rectangles_and_text, _, _  = self.detection.detect_text_from_image(ap_screenshot)

        # If the count is not detected, most likely:
        # 1) mouse cursor or something else is blocking the area where 'ap_area_capture()' takes a screenshot.
        # 2) the 'capture_region' argument in 'ap_area_capture()' is wrong.
        if len(rectangles_and_text) <= 0:
            print("[INFO] Couldn't detect current 'AP' count!")
            return None

        return rectangles_and_text[0][1]


    def get_mp(self):

        mp_screenshot = self.window_capture.mp_area_capture()
        rectangles_and_text, _, _  = self.detection.detect_text_from_image(mp_screenshot)

        # If the count is not detected, most likely:
        # 1) mouse cursor or something else is blocking the area where 'mp_area_capture()' takes a screenshot.
        # 2) the 'capture_region' argument in 'mp_area_capture()' is wrong.
        if len(rectangles_and_text) <= 0:
            print("[INFO] Couldn't detect current 'MP' count!")
            return None

        return rectangles_and_text[0][1]
