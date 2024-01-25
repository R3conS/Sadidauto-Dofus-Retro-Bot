from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from src.bot._interfaces._caution import Caution
from src.bot._interfaces._characteristics import Characteristics
from src.bot._interfaces._connection import Connection
from src.bot._interfaces._information import Information
from src.bot._interfaces._inventory import Inventory
from src.bot._interfaces._main_menu import MainMenu
from src.bot._interfaces._offer_or_invite import OfferOrInvite
from src.bot._interfaces._right_click_menu import RightClickMenu


class Interfaces:

    CAUTION = Caution()
    CHARACTERISTICS = Characteristics()
    CONNECTION = Connection()
    INFORMATION = Information()
    INVENTORY = Inventory()
    MAIN_MENU = MainMenu()
    OFFER_OR_INVITE = OfferOrInvite()
    RIGHT_CLICK_MENU = RightClickMenu()

    @classmethod
    def close_all(cls):
        log.info("Closing all interfaces ...")
        while any(interface.is_open() for interface in cls._get_all_interfaces()):
            for interface in cls._get_all_interfaces():
                if interface.is_open():
                    interface.close()
        log.info("Finished closing all interfaces.")

    @classmethod
    def _get_all_interfaces(cls):
        return [
            cls.CHARACTERISTICS,
            cls.INVENTORY,
            cls.RIGHT_CLICK_MENU,
            cls.OFFER_OR_INVITE,
            cls.MAIN_MENU,
            cls.CAUTION,
            cls.INFORMATION,
            cls.CONNECTION
        ]


if __name__ == "__main__":
    Interfaces.close_all()
