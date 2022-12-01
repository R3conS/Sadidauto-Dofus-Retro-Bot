"""Logic related to 'INITIALIZING' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import os
import time

import pyautogui as pyag

from .botstate_enum import BotState
import bank
import combat as cbt
import data
import detection as dtc
import game_window as gw
import pop_up as pu
import window_capture as wc


class Initializing:
    """Holds various 'INITIALIZING' state methods."""

    # Public class attributes.
    script = None
    character_name = None
    official_version = None
    data_hunting = None
    data_banking = None
    data_monsters = None

    # Private class attributes.
    __state = None

    @classmethod
    def initializing(cls):
        """'INITIALIZING' state logic."""
        gw.GameWindow.character_name = cls.character_name
        gw.GameWindow.official_version = cls.official_version
        cbt.Combat.character_name = cls.character_name

        # Making sure 'Dofus.exe' is launched and char is logged in.
        if gw.GameWindow.check_if_exists():
            gw.GameWindow.resize_and_move()
        else:
            os._exit(1)

        # Loading bot script data.
        if cls.__load_bot_script_data(cls.script):
            log.info(f"Successfully loaded '{cls.script}' script!")

        if cls.official_version:
            if cls.__verify_group():
                log.info("Group verified successfully!")

        if cls.__verify_character_name(cls.character_name):
            log.info("Character's name set correctly!")

        # Passing control to 'CONTROLLER' state.
        log.info("Initialization successful!")
        log.info(f"Changing 'BotState' to: '{BotState.CONTROLLER}' ... ")
        cls.__state = BotState.CONTROLLER
        return cls.__state

    @staticmethod
    def in_group():
        """Check if character is in group."""
        coords = [(908, 120), (913, 115), (902, 117)]
        colors = [(0, 153, 0), (0, 138, 0)]
        pixels = []

        for coord in coords:
            for color in colors:
                px = pyag.pixelMatchesColor(coord[0], coord[1], color)
                pixels.append(px)

        if pixels.count(True) == len(coords):
            return True
        else:
            return False  

    @classmethod
    def __load_bot_script_data(cls, script):
        """
        Load data based on `script`.

        Parameters
        ----------
        script : str
            Name of bot `script`.
        
        Returns
        ----------
        True : bool
            If `script` was loaded successfully.
        NoReturn
            Exits program if `script` is not `str` or if `script` is not
            among valid/available scripts.
        
        """
        if not isinstance(script, str):
            log.critical("Parameter 'script' must be a string!")
            log.critical("Exiting ... ")
            os._exit(1)

        script = script.lower()

        if "af_" in script:

            if script == "af_anticlock":
                hunting = data.scripts.astrub_forest.Hunting.Anticlock.data
            elif script == "af_clockwise":
                hunting = data.scripts.astrub_forest.Hunting.Clockwise.data
            elif script == "af_north":
                hunting = data.scripts.astrub_forest.Hunting.North.data
            elif script == "af_east":
                hunting = data.scripts.astrub_forest.Hunting.East.data
            elif script == "af_south":
                hunting = data.scripts.astrub_forest.Hunting.South.data
            elif script == "af_west":
                hunting = data.scripts.astrub_forest.Hunting.West.data

            cls.data_hunting = hunting
            cls.data_banking = data.scripts.astrub_forest.Banking.data
            cls.data_monsters = dtc.Detection.generate_image_data(
                    data.images.monster.AstrubForest.img_list,
                    data.images.monster.AstrubForest.img_path
                )
            # cls.data_monsters = dtc.Detection.generate_image_data(
            #         image_list=["test_1.png"],
            #         image_path="data\\images\\test\\monster_images\\"
            #     )
            cbt.Combat.data_spell_cast = data.scripts.astrub_forest.Cast.data
            cbt.Combat.data_movement = data.scripts.astrub_forest.Movement.data
            bank.Bank.img_path = data.images.npc.AstrubBanker.img_path
            bank.Bank.img_list = data.images.npc.AstrubBanker.img_list
            return True

        else:
            log.critical(f"Couldn't find script '{script}' in database!")
            log.critical("Exiting ... ")
            os._exit(1)

    @classmethod
    def __verify_character_name(cls, character_name):
        """
        Check if name in characteristics interface matches one that's
        passed in during script startup.

        character_name : str
            Character's name.

        Returns
        ----------
        True : bool
            If names match.
        NoReturn
            Program will exit if names do not match or characteristics
            interface couldn't be opened `attempts_allowed` times.
        
        """
        log.info("Verifying character's name ... ")

        attempts_allowed = 3
        attempts_total = 0

        while attempts_total < attempts_allowed:

            pu.PopUp.deal()

            if pu.PopUp.interface("characteristics", "open"):

                sc = wc.WindowCapture.custom_area_capture((685, 93, 205, 26))
                r_and_t, _, _ = dtc.Detection.detect_text_from_image(sc)
                detected_name = r_and_t[0][1]

                if character_name == detected_name:
                    pu.PopUp.interface("characteristics", "close")
                    return True
                else:
                    log.critical("Invalid character name!")
                    log.critical("Exiting ... ")
                    os._exit(1)

            else:
                attempts_total += 1
        
        else:
            log.critical("Failed to open characteristics interface "
                         f"{attempts_allowed} times!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @classmethod
    def __verify_group(cls):
        """Check if character is in group and close group tab."""
        log.info("Verifying group ... ")

        start_time = time.time()
        timeout = 15

        while time.time() - start_time < timeout:

            if cls.in_group():
                log.info("Character is in group!")
                if cls.__group_tab_check() == "opened":
                    if cls.__group_tab_hide():
                        return True
                else:
                    return True

        else:
            log.critical(f"Failed to verify group in {timeout} seconds!")
            log.critical(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @classmethod
    def __group_tab_hide(cls):
        """Hide group tab if it's open."""
        start_time = time.time()
        timeout = 30

        while time.time() - start_time < timeout:

            pu.PopUp.deal()

            if cls.__group_tab_check() == "opened":
                log.info("Hiding group tab ... ")
                pyag.moveTo(927, 117, duration=0.15)
                pyag.click()
                time.sleep(0.5)
            else:
                log.info("Group tab hidden successfully!")
                return True

        else:
            log.critical(f"Failed to hide group tab in {timeout} seconds!")
            log.critical(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @staticmethod
    def __group_tab_check():
        """Check if group tab is opened or closed."""
        coords = [(908, 142), (910, 138), (915, 142)]
        colors = [(197, 73, 6), (102, 45, 23), (103, 32, 5)]
        pixels = []

        for i in range(len(colors)):
            px = pyag.pixelMatchesColor(coords[i][0], coords[i][1], colors[i])
            pixels.append(px)

        if all(pixels):
            return "opened"
        else:
            return "closed"
