from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep

import cv2
import pyautogui as pyag

from src.screen_capture import ScreenCapture
from src.image_detection import ImageDetection
from src.ocr.ocr import OCR
from src.bot._exceptions import UnrecoverableException


class Recoverer:

    CHOOSE_A_SERVER_AREA = (59, 254, 233, 30)
    CHOOSE_YOUR_CHARACTER_AREA = (61, 300, 226, 32)
    SERVER_NAME_AREAS = [
        (83, 478, 135, 23),
        (243, 478, 135, 23),
        (403, 478, 135, 23),
        (563, 478, 135, 23),
        (723, 478, 135, 23)
    ]
    CHARACTER_NAME_AREAS = [
        (78, 531, 136, 23),
        (239, 531, 135, 23),
        (399, 532, 136, 23),
        (562, 531, 136, 23),
        (725, 531, 136, 23)
    ]

    def __init__(self, character_name: str, server_name: str):
        self._character_name = character_name
        self._server_name = server_name
    
    def recover(self):
        pass

    @classmethod
    def _is_choose_a_server_visible(cls):
        return OCR.get_text_from_image(
            ScreenCapture.custom_area(cls.CHOOSE_A_SERVER_AREA)
        ) == "Choose a server"

    @classmethod
    def _is_choose_your_character_visible(cls):
        return OCR.get_text_from_image(
            ScreenCapture.custom_area(cls.CHOOSE_YOUR_CHARACTER_AREA)
        ) == "Choose your character"

    @staticmethod
    def _read_server_name(name_area):
        area = ScreenCapture.custom_area(name_area)
        area = OCR.convert_to_grayscale(area)
        area = OCR.binarize_image(area, 215)
        area = OCR.resize_image(area, 200, 50)
        return OCR.get_text_from_image(area)

    @staticmethod
    def _read_character_name(name_area):
        area = ScreenCapture.custom_area(name_area)
        area = OCR.convert_to_grayscale(area)
        area = OCR.invert_image(area)
        area = OCR.resize_image(area, area.shape[1] * 5, area.shape[0] * 5)
        area = OCR.dilate_image(area, 2)
        area = OCR.binarize_image(area, 115)
        name = OCR.get_text_from_image(area)
        return name.translate(str.maketrans("", "", ". ,:;'"))

    def _select_character(self, name_area):
        log.info(f"Selecting the character ... ")
        click_coords = ImageDetection.get_rectangle_center_point(name_area)
        pyag.moveTo(*click_coords)
        pyag.click(clicks=2, interval=0.1)

        timeout = 10
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if not self._is_choose_your_character_visible():
                log.info("Successfully chose the character!")
                return
            sleep(0.5)
        else:
            raise UnrecoverableException(
                "Timed out while choosing the character. "
                f"Timeout: {timeout} seconds."
            )

    def _choose_character(self):
        """
        This method can be greatly improved if the name tooltip can be
        read reliably. Explanation as to why the method is currently 
        implemented in this dirty/hacky way:

        Above a certain nickname length Dofus doesn't display the full name
        of the character on the name plate in the character selection screen.
        It varies from 8 to 14 depending on the size of the letters. At the
        point where the name doesn't fit on the name plate, Dofus instead
        displays a '...' which can be hovered over with a mouse to see the 
        full name on a tooltip similar to pods. Best solution would be to read 
        it and compare the contents to the character's name, but it's difficult 
        to read it reliably (at least with tesserocr) due to several reasons:

        1) MAIN REASON: When 'q' and 'j' (qj) are next to each other there's no 
        white space in between their lower halves AT ALL.
        2) Letters are very close to each other in general. Almost no blank space.
        3) Lower halves of letters like 'g, j, p, q, y' are cut off. This
        could be solved by increasing the size of the Dofus client. At certain
        sizes the halves are preserved.
        4) Lower case 'j' and 'i' are barely distinguishable.

        I haven't tested other OCR libraries like PaddleOCR or EasyOCR, but
        they are dependent on a lot of other libraries and it seems like an
        overkill for just this one use case. In addition I found that tesserocr
        is WAY faster on CPU which is important since most of the time the bot
        is going to be running on VMs with no GPU.

        """
        log.info(f"Attempting to choose the character ... ")
        log.info(f"Reading character name plates ... ")
        names = [self._read_character_name(name_area) for name_area in self.CHARACTER_NAME_AREAS]
        names_and_areas = dict(zip(names, self.CHARACTER_NAME_AREAS))

        log.info(f"Looking for character by its full name: '{self._character_name}' ... ")
        for name, area in names_and_areas.items():
            if name == self._character_name:
                log.info(f"Character found!")
                self._select_character(area)
                return
        log.error(f"Failed to find a match by full character name!")

        # Check if the name plate's contents are a substring of the full
        # character name. The names' length on the name plate varies from 
        # 8 to 14 depending on the size of the letters.
        log.info(
            f"Looking for character by checking if the content of the name "
            "plate is a substring of the full character name ... "
        )
        for name, area in names_and_areas.items():
            if name in self._character_name:
                log.info(f"Character found!")
                self._select_character(area)
                return
        log.error(f"Failed to find a match!")

        # In some cases the closest letter to the '...' dots is cut off
        # slightly but it's still being read as a part of the name and most
        # of the time incorrectly. In these cases the above code won't work
        # and the last resort is to check the characters that ALWAYS fit
        # on the name plate (the first 8) regardless of letter size.
        log.info(
            f"Looking for character by checking if the first 8 characters of "
            "the name plate are a substring of the full character name ... "
        )
        for name, area in names_and_areas.items():
            if name[:8] in self._character_name:
                log.info(f"Character found!")
                self._select_character(area)
                return
        log.error(f"Failed to find a match!")

        raise UnrecoverableException(f"Failed to choose the character because a matching name couldn't be found!")


    def _choose_server(self):
        log.info(f"Looking for a server named: '{self._server_name}' ... ")
        for name_area in self.SERVER_NAME_AREAS:
            if self._read_server_name(name_area) == self._server_name:
                log.info(f"Server found! Selecting ... ")
                click_coords = ImageDetection.get_rectangle_center_point(name_area)
                pyag.moveTo(*click_coords)
                pyag.click(clicks=2, interval=0.1)
        
                timeout = 10
                start_time = perf_counter()
                while perf_counter() - start_time <= timeout:
                    # ToDo: Also check if the account gets logged in straight
                    # into the game. This happens when the character is in 
                    # combat and was disconnected during it.
                    if self._is_choose_your_character_visible():
                        log.info(f"Successfully chose server: '{self._server_name}'!")
                        return
                    sleep(0.5)
                else:
                    raise UnrecoverableException(
                        "Timed out while choosing the server. "
                        f"Timeout: {timeout} seconds."
                    )
        raise UnrecoverableException(f"Couldn't find a server named: '{self._server_name}'!")


if __name__ == "__main__":
    recoverer = Recoverer("Longestnamepossibleh", "Semi-like")
    # print(recoverer._read_character_name(recoverer.CHARACTER_NAME_AREAS[0]))
    for name_area in recoverer.CHARACTER_NAME_AREAS:
        print(recoverer._read_character_name(name_area))
    # recoverer._choose_server()
    recoverer._choose_character()
