from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
from time import perf_counter
import os

import cv2
import pyautogui as pyag

from .map_data.getter import Getter as MapDataGetter
from ._vault_actions import VaultActions
from ._status_codes_enum import Status
from src.map_changer.map_changer import MapChanger
from src.detection import Detection
from src.window_capture import WindowCapture


class Banker:

    astrub_zaap_map = "4,-19"
    astrub_bank_map = "4,-16"
    no_recall_maps = [
        "4,-16",
        "4,-17",
        "4,-18",
        "4,-19"
    ]

    def __init__(
            self, 
            set_sub_state_callback: callable, 
            script: str, 
            game_window_title: str
        ):
        self.__set_sub_state_callback = set_sub_state_callback
        self.__game_window_title = game_window_title
        self.__npc_images = self.__load_npc_images()
        self.__movement_data = MapDataGetter.get_data_object(script).get_movement_data()
        self.__was_recall_attempted = False
        self.__is_bank_vault_open = False
        self.__is_depositing_finished = False

    def __load_npc_images(self):
        image_folder_path = "src\\state\\out_of_combat\\sub_state\\banking\\images\\astrub_banker_npc"
        loaded_images = []
        for image in os.listdir(image_folder_path):
            loaded_images.append(cv2.imread(os.path.join(image_folder_path, image), cv2.IMREAD_UNCHANGED))
        return loaded_images

    def __handle_char_not_on_asturb_bank_map(self):
        if not self.__was_recall_attempted:
            if not self.is_char_on_no_recall_map():
                log.info("Character is not on a no-recall map. Attempting to recall ... ")
                if self.does_char_have_recall_potion():
                    self.use_recall_potion()
                    if MapChanger.has_loading_screen_passed():
                        if MapChanger.get_current_map_coords() == self.astrub_zaap_map:
                            log.info("Successfully recalled.")
                            return "sucessfully_recalled"
                    else:
                        log.info("Failed to detect loading screen after recalling.")
                        # ToDo: link to recovery state.
                        return "failed_to_detect_loading_screen_after_recall"
                else:
                    log.info("Character does not have a recall potion.")
                    return "char_doesnt_have_recall_potion"
            else:
                log.info("Character is close to the bank. No need to recall.")
                return "no_need_to_recall"
        else:
            map_coords = MapChanger.get_current_map_coords()
            log.info(f"Running to bank. Current map coords: {map_coords}.")
            MapChanger.change_map(map_coords, self.__movement_data)
            if MapChanger.has_loading_screen_passed():
                return "map_changed_successfully"
            else:
                # ToDo: link to recovery state.
                log.critical("Not implemented!")
                return "failed_to_handle"

    def __handle_char_on_asturb_bank_map_outside(self):
        log.info("Character is outside the bank. Going inside ... ")
        self.go_into_astrub_bank()
        if MapChanger.has_loading_screen_passed():
            if self.is_char_inside_astrub_bank():
                log.info("Successfully entered the bank.")
                return "sucessfully_entered_bank"
            else:
                log.info("Failed to enter the bank.")
                return "failed_to_enter_bank"
        else:
            # ToDo: link to recovery state.
            log.info("Failed to detect loading screen after trying to enter the bank.")
            return "failed_to_enter_bank"

    def __handle_char_on_asturb_bank_map_inside_vault_closed(self):
        if self.is_banker_npc_detected():
            banker_x, banker_y = self.get_banker_npc_coords()
            log.info("Banker NPC detected. Talking with banker ... ")
            self.talk_with_banker(banker_x, banker_y)
            if self.is_banker_dialogue_open():
                log.info("Successfully opened banker dialogue. Opening bank vault ...")
                self.select_consult_your_personal_safe()
                if self.is_bank_vault_open():
                    log.info("Successfully opened bank vault.")
                    return "sucessfully_opened_bank_vault"
                else:
                    log.info("Failed to open bank vault.")
                    return "failed_to_open_bank_vault"
            else:
                log.info("Failed to open banker dialogue.")
                return "failed_to_open_banker_dialogue"
        else:
            log.info("Failed to detect banker NPC.")
            return "failed_to_detect_banker_npc"

    def __handle_char_on_asturb_bank_map_inside_vault_open(self):
        return VaultActions.deposit_all_tabs()

    def bank(self):
        while True:
            if not self.is_char_on_astrub_bank_map():
                status = self.__handle_char_not_on_asturb_bank_map()
                if (
                    status == "sucessfully_recalled"
                    or status == "char_doesnt_have_recall_potion"
                    or status == "no_need_to_recall"
                ):
                    self.__was_recall_attempted = True
                    continue
                elif status == "map_changed_successfully":
                    continue
                elif status == "failed_to_detect_loading_screen_after_recall":
                    log.critical("Not implemented!")
                    # ToDo: link to recovery state.
                    os._exit(1)

            elif self.is_char_on_astrub_bank_map() and not self.is_char_inside_astrub_bank():
                status = self.__handle_char_on_asturb_bank_map_outside()
                if status == "sucessfully_entered_bank":
                    continue
                elif status == "failed_to_enter_bank":
                    log.critical("Not implemented!")
                    # ToDo: link to recovery state.
                    os._exit(1)

            elif (
                self.is_char_on_astrub_bank_map() 
                and self.is_char_inside_astrub_bank()
                and not self.__is_bank_vault_open
                and not self.__is_depositing_finished
            ):
                status = self.__handle_char_on_asturb_bank_map_inside_vault_closed()
                if status == "sucessfully_opened_bank_vault":
                    self.__is_bank_vault_open = True
                    continue
                elif (
                    status == "failed_to_open_bank_vault"
                    or status == "failed_to_open_banker_dialogue" 
                    or status == "failed_to_detect_banker_npc"
                ):
                    log.critical("Not implemented!")
                    # ToDo: link to recovery state.
                    os._exit(1)

            elif (
                self.is_char_on_astrub_bank_map() 
                and self.is_char_inside_astrub_bank()
                and self.__is_bank_vault_open
                and not self.__is_depositing_finished
            ):
                status = self.__handle_char_on_asturb_bank_map_inside_vault_open()
                if status == Status.SUCCESSFULLY_DEPOSITED_ALL_TABS:
                    self.__is_depositing_finished = True
                    continue
                elif status == Status.FAILED_TO_DEPOSIT_ALL_TABS:
                    log.critical("Not implemented!")
                    # ToDo: link to recovery state.
                    os._exit(1)
            
            elif self.__is_depositing_finished:
                status = self.handle_depositing_finished()
                if status == "successfully_left_bank":
                    log.info("Successfully banked.")
                    self.__is_depositing_finished = False
                    self.__is_bank_vault_open = False
                    self.__was_recall_attempted = False
                    # ToDo: Pass control back to the controller/s.
                    os._exit(0)
                elif (
                    status == "failed_to_leave_bank"
                    or status == "failed_to_close_bank_vault"
                ):
                    log.critical("Not implemented!")
                    # ToDo: link to recovery state.
                    os._exit(1)

    @classmethod
    def handle_depositing_finished(cls):
        log.info("Closing the bank vault ... ")
        cls.close_bank_vault()
        if not cls.is_bank_vault_open():
            log.info("Successfully closed the bank vault.")
            log.info("Leaving the bank ... ")
            cls.leave_astrub_bank()
            if MapChanger.has_loading_screen_passed():
                if not cls.is_char_inside_astrub_bank():
                    log.info("Successfully left the bank.")
                    return "successfully_left_bank"
                else:
                    log.info("Failed to leave the bank.")
                    return "failed_to_leave_bank"
            else:
                log.info("Failed to detect loading screen after trying to leave the bank.")
                return "failed_to_leave_bank"
        log.info("Failed to close the bank vault.")
        return "failed_to_close_bank_vault"

    @classmethod
    def is_char_on_no_recall_map(cls):
        return MapChanger.get_current_map_coords() in cls.no_recall_maps

    @staticmethod
    def does_char_have_recall_potion():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)

    @staticmethod
    def use_recall_potion():
        pyag.moveTo(664, 725)
        pyag.click(clicks=2, interval=0.1)

    @classmethod
    def is_char_on_zaap_map(cls):
        return MapChanger.get_current_map_coords() == cls.astrub_bank_map

    @classmethod
    def is_char_on_astrub_bank_map(cls):
        return MapChanger.get_current_map_coords() == cls.astrub_bank_map

    @staticmethod
    def is_char_inside_astrub_bank():
        return all((
            pyag.pixelMatchesColor(10, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(922, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(454, 90, (0, 0, 0)), 
            pyag.pixelMatchesColor(533, 99, (242, 240, 236)),
            pyag.pixelMatchesColor(491, 124, (239, 236, 232))
        ))

    @staticmethod
    def go_into_astrub_bank():
        pyag.keyDown('e')
        pyag.moveTo(792, 203)
        pyag.click()
        pyag.keyUp('e')

    @staticmethod
    def leave_astrub_bank():
        pyag.keyDown('e')
        pyag.moveTo(262, 502)
        pyag.click()
        pyag.keyUp('e')

    def is_banker_npc_detected(self):
        astrub_bank_interior = WindowCapture.gamewindow_capture()
        for banker_image in self.__npc_images:
            result = Detection.find_image(
                haystack=astrub_bank_interior,
                needle=banker_image,
                confidence=0.99,
            )
            if len(result) > 0:
                return True
        return False
    
    def get_banker_npc_coords(self):
        astrub_bank_interior = WindowCapture.gamewindow_capture()
        for banker_image in self.__npc_images:
            result = Detection.find_image(
                haystack=astrub_bank_interior,
                needle=banker_image,
                confidence=0.99,
            )
            if len(result) > 0:
                return Detection.get_rectangle_center_point(result)
        raise ValueError("Failed to find banker npc.")

    def talk_with_banker(self, banker_x, banker_y):
        if "Dofus Retro" in self.__game_window_title:
            pyag.moveTo(banker_x, banker_y)
            pyag.click("right")
        else: # For Abrak private server
            pyag.keyDown("shift")
            pyag.moveTo(banker_x, banker_y)
            pyag.click()
            pyag.keyUp("shift")

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if self.is_banker_dialogue_open():
                return True
        return False

    @staticmethod
    def is_banker_dialogue_open():
        """Astrub banker dialogue interface."""
        return all((
            pyag.pixelMatchesColor(25, 255, (255, 255, 206)),
            pyag.pixelMatchesColor(123, 255, (255, 255, 206))
        ))

    @staticmethod
    def is_bank_vault_open():
        return all ((
            pyag.pixelMatchesColor(218, 170, (81, 74, 60)),
            pyag.pixelMatchesColor(881, 172, (81, 74, 60)),
            pyag.pixelMatchesColor(700, 577, (213, 207, 170)),
            pyag.pixelMatchesColor(31, 568, (213, 207, 170)),
        ))

    @classmethod
    def select_consult_your_personal_safe(cls):
        """Selects the 'Consult your personal safe' option from the banker dialogue."""
        pyag.moveTo(294, 365)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_bank_vault_open():
                return True
        return False

    @classmethod
    def close_bank_vault(cls):
        pyag.moveTo(904, 172)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls.is_bank_vault_open():
                return True
        return False
