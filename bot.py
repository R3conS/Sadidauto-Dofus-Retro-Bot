"""Main bot logic."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import threading

from state.botstate_enum import BotState
from state.initializing import Initializing
from state.controller import Controller
from state.hunting import Hunting
from state.preparing import Preparing
from state.fighting import Fighting
from state.moving import Moving
from state.banking import Banking
import threading_tools as tt
import window_capture as wc


class Bot:
    """
    Main bot class.

    Logic flow is controlled by '__Bot_Thread_run()'.
    
    Methods
    ----------  
    Bot_Thread_start()
        Start bot thread.
    Bot_Thread_stop()
        Stop bot thread.

    """

    # Private class attributes.
    # Stores current map's coordinates.
    __map_coords = None   
    # Stores currently needed map data.
    __data_map = None
    # Stores monster image data.
    __data_monsters = None
    # 'Bot_Thread' threading attributes.
    __Bot_Thread_stopped = False
    __Bot_Thread_thread = None

    def __init__(self,
                 script: str,
                 character_name: str,
                 official_version: bool,
                 bot_state: str = BotState.INITIALIZING):
        """
        Constructor

        Parameters
        ----------
        script : str
            Bot script to load. Available: 'af_anticlock',
            'af_clockwise', 'af_north', 'af_east', 'af_south',
            'af_west'.
        character_name : str
            Character's nickname.
        official_version : bool, optional
            Controls whether on official or private 'Dofus Retro' 
            servers. Official = `True`.
        bot_state : str, optional
            Current state of bot. Defaults to: `BotState.INITIALIZING`.

        """
        self.__state = bot_state
        Initializing.script = script
        Initializing.character_name = character_name
        Initializing.official_version = official_version

    def __Bot_Thread_run(self):
        """Execute this code while bot thread is alive."""
        try:

            while not self.__Bot_Thread_stopped:

                # Makes bot ready to go. Always starts in this state.
                if self.__state == BotState.INITIALIZING:
                    self.__state = Initializing.initializing()
                    self.__data_monsters = Initializing.data_monsters
                    Controller.data_hunting = Initializing.data_hunting
                    Controller.data_banking = Initializing.data_banking
                    Controller.official_version = Initializing.official_version

                # Determines what state to switch to when out of combat.
                elif self.__state == BotState.CONTROLLER:
                    self.__state = Controller.controller()
                    self.__map_coords = Controller.map_coords
                    self.__data_map = Controller.data_map

                # Handles detection and attacking of monsters.
                elif self.__state == BotState.HUNTING:
                    Hunting.data_monsters = self.__data_monsters
                    Hunting.map_coords = self.__map_coords
                    self.__state, Controller.map_searched = Hunting.hunting()

                # Handles combat preparation.
                elif self.__state == BotState.PREPARING:
                    Preparing.map_coords = self.__map_coords
                    Preparing.data_map = self.__data_map
                    self.__state = Preparing.preparing()

                # Handles combat.
                elif self.__state == BotState.FIGHTING:
                    Fighting.map_coords = self.__map_coords
                    Fighting.data_map = self.__data_map
                    Fighting.cell_coords = Preparing.cell_coords
                    Fighting.cell_color = Preparing.cell_color
                    Fighting.cell_select_failed = Preparing.cell_select_failed
                    self.__state = Fighting.fighting()
                            
                # Handles map changing.
                elif self.__state == BotState.MOVING:
                    Moving.map_coords = self.__map_coords
                    Moving.data_map = self.__data_map
                    self.__state, Controller.map_searched = Moving.moving()

                # Handles banking.
                elif self.__state == BotState.BANKING:
                    Banking.map_coords = self.__map_coords
                    Banking.data_map = self.__data_map
                    self.__state = Banking.banking()

        except:

            log.exception("An exception occured!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def Bot_Thread_start(self):
        """Start bot thread."""
        self.__Bot_Thread_stopped = False
        self.__Bot_Thread_thread = threading.Thread(
                target=self.__Bot_Thread_run
            )
        self.__Bot_Thread_thread.start()
        tt.ThreadingTools.wait_thread_start(self.__Bot_Thread_thread)

    def Bot_Thread_stop(self):
        """Stop bot thread."""
        self.__Bot_Thread_stopped = True
        tt.ThreadingTools.wait_thread_stop(self.__Bot_Thread_thread)
