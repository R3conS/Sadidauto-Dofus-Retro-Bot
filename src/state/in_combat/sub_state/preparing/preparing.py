from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time

import pyautogui as pyag

import data
from image_detection import ImageDetection
from screen_capture import ScreenCapture


class Preparing:
    """Holds various 'PREPARING' state methods."""

    # Public class attributes.
    map_coords = None
    data_map = None

    # Private class attributes.
    __state = None
    __tactical_mode = False
    __cell_coords = None
    __cell_color = None

    def __init__(self, controller):
        self.__controller = controller

    def preparing(self):
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
            if not self.__tactical_mode:
                if self.__enable_tactical_mode():
                    self.__tactical_mode = True
            if self.__tactical_mode:
                if check_for_dummy_cells:
                    check_for_dummy_cells = False
                    if self.__check_dummy_cells(self.map_coords, self.data_map):
                        self.__select_dummy_cells()
                else:
                    if self.__select_starting_cell():
                        self.__state = BotState.FIGHTING
                        return self.__state
                    else:
                        continue
        else:
            log.critical(f"Failed to select starting cell in '{allowed_time}' "
                         "seconds!")
            log.critical("Exiting ... ")
            ScreenCapture.on_exit_capture()

    def get_start_cell_color(self, map_coords, database, start_cell_coords):
        cells_list = self.__get_cells_from_database(map_coords, database)
        index = cells_list.index(start_cell_coords)

        if index <= 1:
            return "red"
        elif index >= 2:
            return "blue"

    def __move_char_to_cell(self, cell_coordinates_list):
        # Time to wait after moving character to cell. If omitted,
        # '__check_if_char_moved()' starts checking before 
        # character has time to move and gives false results.
        wait_after_move_char = 0.5

        for cell in cell_coordinates_list:
            log.info(f"MapChanger character to cell: {cell} ... ")
            pyag.moveTo(cell[0], cell[1])
            pyag.click()
            time.sleep(wait_after_move_char)
            if self.__check_if_char_moved(cell):
                self.__cell_coords = cell
                self.__controller.fighting.cell_coords = self.__cell_coords
                return True
        return False

    def __select_starting_cell(self):
        """Select starting cell and start combat."""
        log.info(f"Trying to move character to starting cell ... ")

        failed_attempts = 0
        attempts_allowed = 2
        start_time = time.time()
        timeout = 20

        while time.time() - start_time < timeout:
            cells = self.__get_cells_from_database(self.map_coords, self.data_map)
            e_cells = self.__get_empty_cells(cells)
            if len(e_cells) <= 0:
                self.map_coords = self.__controller.moving.get_coordinates(self.data_map)
                continue
            if self.__move_char_to_cell(e_cells):
                self.__cell_color = self.get_start_cell_color(
                    self.map_coords,
                    self.data_map,
                    self.__cell_coords
                )
                self.__controller.fighting.cell_color = self.__cell_color
                if self.__start_combat():
                    log.info(f"Successfully selected starting cell!")
                    return "combat_start"
            else:
                if failed_attempts < attempts_allowed:
                    self.map_coords = self.__controller.moving.get_coordinates(self.data_map)
                    failed_attempts += 1
                    continue
                else:
                    log.error("Cell selection failed!")
                    log.info("Trying to start combat ... ")
                    if self.__start_combat():
                        self.__controller.fighting.cell_select_failed = True
                        return "selection_fail"
        else:
            log.error(f"Timed out in '__select_starting_cell()'!")
            log.error("Cell selection failed!")
            log.info("Trying to start combat ... ")
            if self.__start_combat():
                self.__controller.fighting.cell_select_failed = True
                return "selection_fail"

    def __select_dummy_cells(self):
        log.info("Trying to move character to dummy cell ... ")

        failed_attempts = 0
        attempts_allowed = 1
        start_time = time.time()
        timeout = 20

        while time.time() - start_time < timeout:

            cells = self.__get_dummy_cells(self.map_coords, self.data_map)
            e_cells = self.__get_empty_cells(cells)

            if len(e_cells) <= 0:
                self.map_coords = self.__controller.moving.get_coordinates(self.data_map)
                continue

            if self.__move_char_to_cell(e_cells):
                log.info("Successfully moved character to dummy cell!")
                return True

            else:

                if failed_attempts < attempts_allowed:
                    self.map_coords = self.__controller.moving.get_coordinates(self.data_map)
                    failed_attempts += 1
                    continue
                else:
                    log.error("Failed to move character to dummy cell!")
                    return False

        else:
            log.error(f"Timed out in '__select_dummy_cells()'!")
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
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    cell_coordinates_list = i_value["cell"]
                    return cell_coordinates_list

    @staticmethod
    def __get_empty_cells(cell_coordinates_list):
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
        wait_combat_start = 9
        # 'Ready' button state.
        ready_button_clicked = False
        # Controls if clicking 'Ready' first time. Will click twice
        # after failing the first time.
        first_try = True
        # Loop control variables.
        timeout = 30
        start_time = time.time()

        # Clicking 'Ready' to start combat.
        while time.time() - start_time < timeout:

            # If 'Ready' button wasn't clicked.
            if not ready_button_clicked:

                log.info("Clicking 'Ready' ... ")
                pyag.moveTo(865, 565, duration=0.15)
                if first_try:
                    pyag.click()
                else:
                    pyag.click(clicks=2, interval=0.1)
                # MapChanger the mouse off the 'Ready' button in case it 
                # needs to be detected again.
                pyag.move(0, 80)
                click_time = time.time()
                ready_button_clicked = True 

            # Checking if combat started after 'Ready' was clicked.
            if ready_button_clicked:

                screenshot = ScreenCapture.game_window()
                cc_icon = ImageDetection.find_image(
                        screenshot,
                        data.images.Status.fighting_sv_1,
                        confidence=0.8
                    )
                ap_icon = ImageDetection.find_image(
                        screenshot, 
                        data.images.Status.fighting_sv_2,
                        confidence=0.8
                    )
                mp_icon = ImageDetection.find_image(
                        screenshot,
                        data.images.Status.fighting_sv_3,
                        confidence=0.8
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
        
        else:
            log.error(f"Timed out in '__start_combat()!")
            log.error(f"'Dofus' preparation stage time ran out!")
            log.error(f"Assuming that combat has started ... ")
            return True
