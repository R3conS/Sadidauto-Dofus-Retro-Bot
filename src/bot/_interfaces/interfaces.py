from src.logger import get_logger

log = get_logger()

from src.bot._interfaces._bank_vault import BankVault
from src.bot._interfaces._banker_dialogue import BankerDialogue
from src.bot._interfaces._caution.caution import Caution
from src.bot._interfaces._characteristics import Characteristics
from src.bot._interfaces._connection.connection import Connection
from src.bot._interfaces._fight_results.fight_results import FightResults
from src.bot._interfaces._information import Information
from src.bot._interfaces._inventory import Inventory
from src.bot._interfaces._login_screen.login_screen import LoginScreen
from src.bot._interfaces._main_menu.main_menu import MainMenu
from src.bot._interfaces._offer_or_invite._offer_or_invite import OfferOrInvite
from src.bot._interfaces._right_click_menu.right_click_menu import RightClickMenu


class Interfaces:

    _instance = None
    BANK_VAULT = None
    BANKER_DIALOGUE = None
    CAUTION = Caution()
    CHARACTERISTICS = Characteristics()
    CONNECTION = Connection()
    FIGHT_RESULTS = FightResults()
    INFORMATION = Information()
    INVENTORY = Inventory()
    LOGIN_SCREEN = LoginScreen()
    MAIN_MENU = MainMenu()
    OFFER_OR_INVITE = OfferOrInvite()
    RIGHT_CLICK_MENU = RightClickMenu()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self, script: str, game_window_title: str):
        Interfaces.BANK_VAULT = BankVault(script, game_window_title)
        Interfaces.BANKER_DIALOGUE = BankerDialogue(script, game_window_title)

    @classmethod
    def close_all(cls):
        log.info("Closing all interfaces ...")
        while any(interface.is_open() for interface in cls._get_all_closable_interfaces()):
            for interface in cls._get_all_closable_interfaces():
                if interface.is_open():
                    try:
                        interface.close()
                    except AttributeError:
                        interface.click_no()
        log.info("Finished closing all interfaces.")

    @classmethod
    def _get_all_closable_interfaces(cls):
        return [
            cls.BANK_VAULT,
            cls.BANKER_DIALOGUE,
            cls.CHARACTERISTICS,
            cls.INVENTORY,
            cls.RIGHT_CLICK_MENU,
            cls.OFFER_OR_INVITE,
            cls.MAIN_MENU,
            cls.CAUTION,
            cls.INFORMATION,
            cls.CONNECTION,
            cls.FIGHT_RESULTS
        ]


if __name__ == "__main__":
    interfaces = Interfaces("af_anticlock", "Dofus Retro")
    interfaces.OFFER_OR_INVITE.close()
