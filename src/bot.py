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

                # Determines what state to switch to when out of combat.
                elif self.__state == BotState.CONTROLLER:
                    self.__state = Controller.controller()

                # Handles detection and attacking of monsters.
                elif self.__state == BotState.HUNTING:
                    self.__state = Hunting.hunting()

                # Handles combat preparation.
                elif self.__state == BotState.PREPARING:
                    self.__state = Preparing.preparing()

                # Handles combat.
                elif self.__state == BotState.FIGHTING:
                    self.__state = Fighting.fighting()
                            
                # Handles map changing.
                elif self.__state == BotState.MOVING:
                    self.__state = Moving.moving()

                # Handles banking.
                elif self.__state == BotState.BANKING:
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
