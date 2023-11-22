from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import os

import pygetwindow as gw

from .botstate_enum import BotState
import bank
import combat as cbt
import data
import detection as dtc
from pop_up import PopUp
import state
import window_capture as wc


class Initializing:

    script = None
    character_name = None
    official_version = None

    __window_suffixes = ["Dofus Retro", "Abrak"]
    __window_size = (950, 785)
    __window_pos = (-8, 0)

    @classmethod
    def initializing(cls):
        log.info("Starting initialization ... ")
        cls.__prepare_game_window()
        cls.__load_bot_script_data(cls.script)
        cls.__verify_character_name(cls.character_name)
        log.info("Initialization successful!")
        return BotState.CONTROLLER

    @classmethod
    def __prepare_game_window(cls):
        log.info("Attempting to prepare Dofus window ... ")
        if bool(gw.getWindowsWithTitle(cls.character_name)):
            for w in gw.getWindowsWithTitle(cls.character_name):
                if any(suffix in w.title for suffix in cls.__window_suffixes):
                    w.restore()
                    w.activate()
                    w.resizeTo(*cls.__window_size)
                    w.moveTo(*cls.__window_pos)
                    log.info(f"Successfully prepared '{w.title}' Dofus window!")
                    return
        log.critical(f"Failed to detect Dofus window for '{cls.character_name}'! Exiting ...")
        os._exit(1)

    @classmethod
    def __load_bot_script_data(cls, script):
        log.info("Attempting to load bot script data ... ")

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

            state.Controller.data_hunting = hunting
            state.Controller.data_banking = data.scripts.astrub_forest.Banking.data

            state.Hunting.data_monsters = dtc.Detection.generate_image_data(
                    data.images.monster.AstrubForest.img_list,
                    data.images.monster.AstrubForest.img_path
                )
            # state.Hunting.data_monsters = dtc.Detection.generate_image_data(
            #         image_list=["test_1.png"],
            #         image_path="data\\images\\test\\monster_images\\"
            #     )

            cbt.Combat.data_spell_cast = data.scripts.astrub_forest.Cast.data
            cbt.Combat.data_movement = data.scripts.astrub_forest.Movement.data
            cbt.Combat.character_name = cls.character_name

            bank.Bank.img_path = data.images.npc.AstrubBanker.img_path
            bank.Bank.img_list = data.images.npc.AstrubBanker.img_list
            return

        log.critical(f"Couldn't find script '{script}' in database! Exiting ... ")
        os._exit(1)

    @classmethod
    def __verify_character_name(cls, character_name):
        log.info("Verifying character's name ... ")
        attempts_allowed = 3
        attempts_total = 0
        while attempts_total < attempts_allowed:
            PopUp.deal()
            if PopUp.interface("characteristics", "open"):
                sc = wc.WindowCapture.custom_area_capture((685, 93, 205, 26))
                r_and_t, _, _ = dtc.Detection.detect_text_from_image(sc)
                if character_name == r_and_t[0][1]:
                    PopUp.interface("characteristics", "close")
                    return True
                else:
                    log.critical("Invalid character name! Exiting ... ")
                    os._exit(1)
            else:
                attempts_total += 1
        else:
            log.critical(
                f"Failed to open characteristics interface {attempts_allowed} times!"
                "Exiting ..."
            )
            wc.WindowCapture.on_exit_capture()
