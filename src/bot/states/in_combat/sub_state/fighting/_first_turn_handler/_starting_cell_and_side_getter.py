from math import sqrt

from src.bot.map_changer.map_changer import MapChanger
from ..map_data.getter import Getter as FightingDataGetter


class Getter:

    def __init__(self, script: str):
        self._starting_cells = FightingDataGetter.get_data_object(script).get_starting_cells()

    def get_starting_cell_coords(self, character_pos):
        map_coords = MapChanger.get_current_map_coords()
        starting_cells = self._get_starting_cells(map_coords)
        return self._get_closest_cell(character_pos, starting_cells)

    def get_starting_side_color(self, character_pos):
        map_coords = MapChanger.get_current_map_coords()
        starting_cells = self._get_starting_cells(map_coords)
        closest_cell = self._get_closest_cell(character_pos, starting_cells)
        for map, cell_data in self._starting_cells.items():
            if map_coords == map:
                for color, cell_coords_list in cell_data.items():
                    for cell_coords in cell_coords_list:
                        if cell_coords == closest_cell:
                            return color
        raise Exception(f"No color found for cell {closest_cell} on map {map_coords}.")

    def _get_starting_cells(self, map_coords: str):
        starting_cells = []
        for map, cell_data in self._starting_cells.items():
            if map_coords == map:
                for _, cell_coords_list in cell_data.items():
                    for cell_coords in cell_coords_list:
                        starting_cells.append(cell_coords)
        return starting_cells

    def _get_closest_cell(self, cell_pos, cells_list):
        closest_cell = cells_list[0]
        closest_cell_distance = self._get_distance_between_cells(cell_pos, closest_cell)
        for cell in cells_list:
            distance = self._get_distance_between_cells(cell_pos, cell)
            if distance < closest_cell_distance:
                closest_cell = cell
                closest_cell_distance = distance
        return closest_cell

    def _get_distance_between_cells(self, cell_1, cell_2):
        return sqrt((cell_2[0] - cell_1[0])**2 + (cell_2[1] - cell_1[1])**2)
