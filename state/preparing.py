"""Logic related to 'PREPARING' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import time

import pyautogui as pyag

from .botstate_enum import BotState
import data
import detection as dtc
import state
import window_capture as wc


class Preparing:
    """Holds various 'PREPARING' state methods."""

    # Public class attributes.
    map_coords = None
    data_map = None
    cell_coords = None
    cell_color = None
    cell_select_failed = False

    # Private class attributes.
    __state = None
    __tactical_mode = False

    @classmethod
    def preparing(cls):
        """'PREPARING' state logic."""
        # Stores whether to check for dummy cells. Always checks on
        # first iteration of loop.
        check_for_dummy_cells = True
        # Loop control variables.
        start_time = time.time()
        allowed_time = 45
        # Giving time for monsters to load before starting to check for 
        # empty cells. If ommited, may return false empty cell values
        # on first iteration of loop.
        time.sleep(0.5)

        while time.time() - start_time < allowed_time:

            if not cls.__tactical_mode:
                if cls.__enable_tactical_mode():
                    cls.__tactical_mode = True

            if cls.__tactical_mode:

                if check_for_dummy_cells:

                    check_for_dummy_cells = False
                    if cls.__check_dummy_cells(cls.map_coords, cls.data_map):
                        cls.__select_dummy_cells()

                else:

                    if cls.__select_starting_cell():
                        cls.__state = BotState.FIGHTING
                        return cls.__state
                    else:
                        continue

        else:
            log.critical(f"Failed to select starting cell in '{allowed_time}' "
                         "seconds!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @classmethod
    def get_start_cell_color(cls, map_coords, database, start_cell_coords):
        """
        Get combat start cell color.

        Parameters
        ----------
        map_coords : str
            Map's coordinates as `str`.
        database : list[dict]
            `list` of `dict` from script's 'Hunting.data'.
        start_cell_coords : Tuple[int, int]
            Starting cell's (x, y) coordinates.

        Returns
        ----------
        str
            Color of starting cell.

        """
        cells_list = cls.__get_cells_from_database(map_coords, database)
        index = cells_list.index(start_cell_coords)

        if index <= 1:
            return "red"
        elif index >= 2:
            return "blue"

    @classmethod
    def __move_char_to_cell(cls, cell_coordinates_list):
        """
        Move character to cell.

        Also saves the starting cell coordinates for use in "FIGHTING"
        state.
        
        Parameters
        ----------
        cell_coordinates_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of cells.

        Returns
        ----------
        True : bool
            If character was moved successfully.
        False : bool
            If character wasn't moved.
        
        """
        # Time to wait after moving character to cell. If omitted,
        # '__check_if_char_moved()' starts checking before 
        # character has time to move and gives false results.
        wait_after_move_char = 0.5

        for cell in cell_coordinates_list:
            log.info(f"Moving character to cell: {cell} ... ")
            pyag.moveTo(cell[0], cell[1])
            pyag.click()
            time.sleep(wait_after_move_char)
            if cls.__check_if_char_moved(cell):
                cls.cell_coords = cell
                return True
        return False

    @classmethod
    def __select_starting_cell(cls):
        """Select starting cell and start combat."""
        failed_attempts = 0
        attempts_allowed = 2

        log.info(f"Trying to move character to starting cell ... ")

        while True:

            cells = cls.__get_cells_from_database(cls.map_coords, cls.data_map)
            e_cells = cls.__get_empty_cells(cells)

            if len(e_cells) <= 0:
                cls.map_coords = state.Moving.get_coordinates(cls.data_map)
                continue

            if cls.__move_char_to_cell(e_cells):

                cls.cell_color = cls.get_start_cell_color(cls.map_coords,
                                                          cls.data_map,
                                                          cls.cell_coords)

                if cls.__start_combat():
                    log.info(f"Successfully selected starting cell!")
                    return "combat_start"

            else:

                if failed_attempts < attempts_allowed:
                    cls.map_coords = state.Moving.get_coordinates(cls.data_map)
                    failed_attempts += 1
                    continue

                else:
                    log.error("Cell selection failed!")
                    log.info("Trying to start combat ... ")
                    if cls.__start_combat():
                        cls.cell_select_failed = True                           
                        return "selection_fail"

    @classmethod
    def __select_dummy_cells(cls):
        """
        Select dummy cell to make starting cells visible.
        
        On certain maps character might spawn on a starting cell and
        block visibility of another starting cell. This method moves
        character out of the way so that all starting cells are visible.

        """
        failed_attempts = 0
        attempts_allowed = 1

        log.info("Trying to move character to dummy cell ... ")

        while True:

            cells = cls.__get_dummy_cells(cls.map_coords, cls.data_map)
            e_cells = cls.__get_empty_cells(cells)

            if len(e_cells) <= 0:
                cls.map_coords = state.Moving.get_coordinates(cls.data_map)
                continue

            if cls.__move_char_to_cell(e_cells):
                log.info("Successfully moved character to dummy cell!")
                return True

            else:

                if failed_attempts < attempts_allowed:
                    cls.map_coords = state.Moving.get_coordinates(cls.data_map)
                    failed_attempts += 1
                    continue
                else:
                    log.error("Failed to move character to dummy cell!")
                    return False

    @staticmethod
    def __check_dummy_cells(map_coords, database):
        """Check if map has dummy cells."""

        log.info("Checking for dummy cells ... ")

        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    if "d_cell" in i_value.keys():
                        log.info("Dummy cells available!")
                        return True
                    else:
                        log.info("No dummy cells available on this map!")
                        return False

    @staticmethod
    def __get_dummy_cells(map_coords, database):
        """Get current map's dummy cells."""
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    cell_coordinates_list = i_value["d_cell"]
                    return cell_coordinates_list

    @staticmethod
    def __get_cells_from_database(map_coords, database):
        """
        Get map's starting cell coordinates from database.
        
        Parameters
        ----------
        map_coords : str
            Map's coordinates as `str`.
        database : list[dict]
            `list` of `dict` from script's 'Hunting.data'.
        
        Returns
        ----------
        cell_coordinates_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of cells.
        
        """
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    cell_coordinates_list = i_value["cell"]
                    return cell_coordinates_list

    @staticmethod
    def __get_empty_cells(cell_coordinates_list):
        """
        Get empty cell coordinates from cell coordinates list.

        Logic
        ----------
        - Check for red and blue pixels on every (x, y) coordinate in
        `cell_coordinates_list`.
        - Append every coordinate where pixels were found to 
        `empty_cells_list`

        Parameters
        ----------
        cell_coordinates_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of cells.
        
        Returns
        ----------
        empty_cells_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of empty
            cells.
        
        """
        empty_cells_list = []
        colors = [(255, 0, 0), (154, 0, 0), (0, 0, 255), (0, 0, 154)]

        for coords in cell_coordinates_list:
            for color in colors:
                px = pyag.pixelMatchesColor(coords[0], coords[1], color)
                if px:
                    empty_cells_list.append(coords)

        return empty_cells_list

    @staticmethod
    def __enable_tactical_mode():
        """Enable tactical mode."""
        # Wait time after clicking on 'Tactical Mode' icon. Giving time
        # for green check mark to appear.
        wait_time_click = 0.25
        # Colors.
        c_green = (0, 153, 0)
        c_gray = (216, 202, 150)
        # Loop control variables.
        start_time = time.time()
        wait_time = 7

        while time.time() - start_time < wait_time:

            group = pyag.pixelMatchesColor(818, 526, c_gray)

            if group:
                tactical_mode = pyag.pixelMatchesColor(790, 526, c_green)
                if not tactical_mode:
                    log.info("Enabling 'Tactical Mode' ... ")
                    pyag.moveTo(790, 526, duration=0.15)
                    pyag.click()
                    time.sleep(wait_time_click)
                else:
                    log.info("'Tactical Mode' enabled!")
                    return True

            else:
                tactical_mode = pyag.pixelMatchesColor(817, 524, c_green)
                if not tactical_mode:
                    log.info("Enabling 'Tactical Mode' ... ")
                    pyag.moveTo(817, 524, duration=0.15)
                    pyag.click()
                    time.sleep(wait_time_click)
                else:
                    log.info("'Tactical Mode' enabled!")
                    return True

        else:
            log.error(f"Failed to enable in {wait_time} seconds!")
            return False

    @staticmethod
    def __check_if_char_moved(cell_coordinates):
        """
        Check if character moved to cell.

        Checks for red and blue colored pixels on `cell_coordinates`. If
        none were found it means character is standing there.
        
        Parameters
        ----------
        cell_coordinates : Tuple[int, int]

        Returns
        ----------
        True : bool
            If character was moved successfully.
        False : bool
            If character wasn't moved.
        
        """
        pixels = []
        colors = [
            (255, 0, 0), (154, 0, 0), (0, 0, 255), (0, 0, 154), (85, 81, 56)
        ]
        
        for color in colors:
            px = pyag.pixelMatchesColor(cell_coordinates[0],
                                             cell_coordinates[1],
                                             color)
            pixels.append(px)

        if not any(pixels):
            log.info("Character moved successfully!")
            return True
        else:
            log.info("Failed to move character!")
            return False

    @staticmethod
    def __start_combat():
        """Click ready to start combat."""
        # Time to wait after clicking ready. How long to keep chacking 
        # if combat was started successfully.
        wait_combat_start = 5
        # 'Ready' button state.
        ready_button_clicked = False
        # Controls if clicking 'Ready' first time. Will click twice
        # after failing the first time.
        first_try = True
        # Loop control variables.
        timeout = 15
        start_time = time.time()

        # Getting (x, y) coords of 'Ready' button.
        while time.time() - start_time < timeout:

            screenshot = wc.WindowCapture.gamewindow_capture()
            ready_button_icon = dtc.Detection.get_click_coords(
                    dtc.Detection.find(
                            screenshot,
                            data.images.Status.preparing_sv_2,
                            threshold=0.8
                        )
                    )

            if len(ready_button_icon) > 0:
                x, y = ready_button_icon[0][0], ready_button_icon[0][1]
                break

        else:
            log.critical(f"Failed to locate 'Ready' button!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

        # Clicking 'Ready' to start combat.
        while True:

            # If 'Ready' button wasn't clicked.
            if not ready_button_clicked:

                log.info("Clicking 'READY' ... ")
                pyag.moveTo(x, y, duration=0.15)
                if first_try:
                    pyag.click()
                else:
                    pyag.click(clicks=2, interval=0.1)
                # Moving the mouse off the 'Ready' button in case it 
                # needs to be detected again.
                pyag.move(0, 80)
                click_time = time.time()
                ready_button_clicked = True 

            # Checking if combat started after 'Ready' was clicked.
            if ready_button_clicked:

                screenshot = wc.WindowCapture.gamewindow_capture()
                cc_icon = dtc.Detection.find(
                        screenshot,
                        data.images.Status.fighting_sv_1,
                        threshold=0.8
                    )
                ap_icon = dtc.Detection.find(
                        screenshot, 
                        data.images.Status.fighting_sv_2,
                        threshold=0.8
                    )
                mp_icon = dtc.Detection.find(
                        screenshot,
                        data.images.Status.fighting_sv_3,
                        threshold=0.8
                    )
                
                if time.time() - click_time > wait_combat_start:
                    log.error("Failed to start combat!")
                    log.error("Retrying ... ")
                    ready_button_clicked = False
                    first_try = False
                    continue

                if len(cc_icon) > 0 and len(ap_icon) > 0 and len(mp_icon) > 0:
                    log.info("Successfully started combat!")
                    return True

