from src.logger import get_logger

log = get_logger()

from time import sleep

import cv2
import pyautogui as pyag

from src.bot._exceptions import RecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.utilities.general import load_image, move_mouse_off_game_area
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class HpRecoverer:

    IMAGE_DIR_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_hp_recoverer\\_images"

    SIT_ICON_IMAGES = [
        load_image(IMAGE_DIR_PATH, "sit_official.png"),
        load_image(IMAGE_DIR_PATH, "sit_abrak.png")
    ]

    @classmethod
    def recover_all_health_by_sitting(cls):
        log.info("Recovering all health by sitting ... ")

        Interfaces.CHARACTERISTICS.open()
        cls._click_sit_icon()

        while Interfaces.CHARACTERISTICS.is_open():
            health_row_text = cls._read_health_points_row()
            current_health, max_health = cls._parse_health_points_row_text(health_row_text)
            log.info(f"Recovering... Health points: ({current_health}/{max_health}).")
            if current_health == max_health:
                log.info("Successfully recovered all health!")
                Interfaces.CHARACTERISTICS.close()
                return
            sleep(5)
        else:
            raise RecoverableException("Characteristics interface is not open.")

    @staticmethod
    def is_health_bar_visible():
        if all((
            pyag.pixelMatchesColor(525, 597, (255, 255, 255)),
            pyag.pixelMatchesColor(498, 607, (255, 255, 255)),
            pyag.pixelMatchesColor(551, 607, (255, 255, 255)),
            pyag.pixelMatchesColor(524, 639, (255, 255, 255))
        )) or all((
            pyag.pixelMatchesColor(525, 597, (230, 230, 230)),
            pyag.pixelMatchesColor(498, 607, (230, 230, 230)),
            pyag.pixelMatchesColor(551, 607, (230, 230, 230)),
            pyag.pixelMatchesColor(524, 639, (230, 230, 230))
        )):
            return True
        return False

    @staticmethod
    def is_health_bar_full():
        if (
            pyag.pixelMatchesColor(512, 595, (235, 128, 128))
            or pyag.pixelMatchesColor(512, 595, (212, 115, 115))
        ):
            return True
        return False

    @staticmethod
    def _read_health_points_row() -> str:
        """Read health points row in Characteristics interface."""
        sc = ScreenCapture.custom_area((780, 206, 120, 23))
        sc = OCR.resize_image(sc, sc.shape[1] * 3, sc.shape[0] * 3)
        sc = OCR.convert_to_grayscale(sc)
        return OCR.get_text_from_image(sc)

    @staticmethod
    def _parse_health_points_row_text(text: str) -> tuple[int, int]:
        """
        Gets the nominator and denominator from the health points row text.

        Expected format: nominator / denominator
        """
        if "/" not in text:
            raise ValueError(f"Incorrect format. Expected: 'number / number'. Received: '{text}'.")
        else:
            split_text = text.split("/")
            split_text = [text.strip() for text in split_text]

            type_casted_text = []
            for text in split_text:
                if not text.isdigit():
                    raise ValueError("Only strings representing numbers allowed.")
                type_casted_text.append(int(text))
            
            return type_casted_text[0], type_casted_text[1]

    @classmethod
    def _get_sit_icon_pos(cls):
        sit_icon_area = (0, 594, 110, 27)
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area(sit_icon_area),
            needles=cls.SIT_ICON_IMAGES,
            confidence=0.98,
            method=cv2.TM_SQDIFF_NORMED
        )
        if len(rectangles) > 0:
            center_point = ImageDetection.get_rectangle_center_point(rectangles[0])
            return center_point[0] + sit_icon_area[0], center_point[1] + sit_icon_area[1]
        return None

    @classmethod
    def _click_sit_icon(cls):
        pos = cls._get_sit_icon_pos()
        if pos is not None:
            pyag.moveTo(pos[0], pos[1])            
            pyag.click()
            move_mouse_off_game_area() # Move mouse off the icon so that its tooltip disappears.
        else:
            raise RecoverableException("Failed to get 'Sit' icon position.")


if __name__ == "__main__":
    HpRecoverer.recover_all_health_by_sitting()
