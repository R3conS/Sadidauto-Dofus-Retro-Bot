from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from time import perf_counter, sleep

import numpy as np
from pyautogui import pixelMatchesColor

from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._recoverer._reconnecter._character_selector import CharacterSelector
from src.bot._recoverer._reconnecter._game_window import get_game_window, resize_game_window
from src.bot._recoverer._reconnecter._login_clicker import LoginClicker
from src.bot._recoverer._reconnecter._server_selector import ServerSelector
from src.bot._states.in_combat._sub_states.sub_states_enum import State as InCombat_SubState
from src.bot._states.in_combat._sub_states.fighting._spells.spells import Spells
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class Reconnecter:

    def __init__(
        self, 
        character_name: str, 
        server_name: str,
        character_level: int,
        game_window_identifier: int | str, # String (title) only used for dev/testing.
        game_window_default_size: tuple[int, int] # Set in initializer.py.
    ):
        self._character_name = character_name
        self._server_name = server_name
        self._character_level = character_level
        self._game_window = get_game_window(game_window_identifier)
        self._game_window_default_size = game_window_default_size
        self._login_clicker = LoginClicker(game_window_identifier)
        self._server_selector = ServerSelector(server_name, game_window_identifier)
        self._character_selector = CharacterSelector(character_name, character_level, game_window_identifier)

    def reconnect(self, disconnect_occured_in_sub_state: InCombat_SubState = None):
        max_attempts = 3
        total_attempts = 0
        while total_attempts < max_attempts:
            try:
                log.info(f"({total_attempts + 1}/{max_attempts}) Attempting to reconnect ...")
                if self._login_clicker.is_on_login_screen():
                    self._login_clicker.login()
                if self._server_selector.is_on_server_selection_screen():
                    self._server_selector.select_server()
                if self._character_selector.is_on_character_selection_screen():
                    self._character_selector.select_character()
                if self._is_account_connected():
                    if self._game_window.size != self._game_window_default_size:
                        resize_game_window(self._game_window, self._game_window_default_size)
                    self._wait_for_map_and_minimap_to_load()
                    if disconnect_occured_in_sub_state == InCombat_SubState.PREPARING:
                        self._wait_chat_message_online_and_in_the_fight_to_load()
                    elif disconnect_occured_in_sub_state == InCombat_SubState.FIGHTING:
                        # ToDo: If the fight ends during disconnection
                        # the spell icons will never load and RecoverableException
                        # will keep getting raised. This will inevitably cause
                        # an UnrecoverableException to be raised. Need to find
                        # a way to fix this. Can just reset 'disconnect_occured_in_sub_state'
                        # to None before waiting, but this seems like a hacky solution.
                        self._wait_for_spell_icons_to_load()
                    log.info("Successfully reconnected!")
                    break
                total_attempts += 1
            except RecoverableException:
                total_attempts += 1
                log.error("Failed to reconnect!")
        else:
            raise UnrecoverableException(f"Failed to reconnect in '{max_attempts}' attempts.")

    @staticmethod
    def _is_account_connected():
        """If chat, minimap, spell/item bar, interface icons etc. are not visible."""
        return (
            pixelMatchesColor(673, 747, (213, 207, 170))
            # Color is different when an offer (exchange, group invite, etc.) is on screen.
            or pixelMatchesColor(673, 747, (192, 186, 153))
        )

    @staticmethod
    def _has_map_loaded():
        """
        Map is the game area where the character can move around. It's 
        considered loaded when there is at least one non-black pixel in
        the search areas.
        """
        sc = ScreenCapture.game_window()
        search_areas = [
            sc[90:170, 5:900], # (x5, y90, w900, h170)
            sc[450:530, 5:900], # (x5, y450, w900, h170)
            sc[90:500, 5:150] # (x5, y90, w150, h500)
        ]
        for area in search_areas:
            if np.any(area != 0):
                return True
        return False

    @staticmethod
    def _has_minimap_loaded():
        sc = ScreenCapture.game_window()
        pixels = [ # sc[y, x]
            sc[667, 501],
            sc[667, 548],
            sc[692, 501],
            sc[692, 548]
        ]
        return any(np.all(pixel[::-1] != (242, 144, 110)) for pixel in pixels)

    @classmethod
    def _wait_for_map_and_minimap_to_load(cls):
        log.info("Waiting for the map and minimap to load ... ")
        timeout = 30
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._has_map_loaded() and cls._has_minimap_loaded():
                log.info("Map and minimap have loaded!")
                return
            sleep(0.25)
        raise RecoverableException(
            "Failed to detect if map and minimap have loaded. "
            f"Timed out: {timeout} seconds."
        )

    @staticmethod
    def _is_chat_message_online_and_in_the_fight_visible():
        chat_sc = ScreenCapture.custom_area((0, 616, 443, 112))
        chat_sc = OCR.convert_to_grayscale(chat_sc)
        chat_sc = OCR.resize_image(chat_sc, chat_sc.shape[1] * 2, chat_sc.shape[0] * 2)
        chat_sc = OCR.binarize_image(chat_sc, 160)
        return "is back online and in the fight" in OCR.get_text_from_image(chat_sc)

    @classmethod
    def _wait_chat_message_online_and_in_the_fight_to_load(cls):
        log.info("Waiting for chat message 'is back online and in the fight' to load ... ")
        timeout = 15
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._is_chat_message_online_and_in_the_fight_visible():
                log.info("Chat message 'is back online and in the fight' has loaded!")
                return
            sleep(0.25)
        raise RecoverableException(
            "Failed to detect if chat message 'is back online and in the fight' has loaded. "
            f"Timed out: {timeout} seconds."
        )
    
    @staticmethod
    def _are_spell_icons_loaded():
        for spell in Spells.get_all():
            if spell.get_icon_pos() is not None:
                return True
        return False

    @classmethod
    def _wait_for_spell_icons_to_load(cls):
        log.info("Waiting for spell icons to load ... ")
        timeout = 10
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._are_spell_icons_loaded():
                log.info("Spell icons have loaded!")
                return
            sleep(0.25)
        raise RecoverableException(
            "Failed to detect if spell icons have loaded. "
            f"Timed out: {timeout} seconds."
        )


if __name__ == "__main__":
    reconnecter = Reconnecter("Juni", "Semi-like", 65, "Abrak", (950, 785))
    # reconnecter = Reconnecter("Kofas", "Boune", 65, "Dofus Retro", (950, 785))
    # reconnecter.reconnect()
