from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from src.bot._interfaces.interfaces import Interfaces
from src.bot._states.out_of_combat._sub_states.banking._vault._tabs.equipment_tab import EquipmentTab
from src.bot._states.out_of_combat._sub_states.banking._vault._tabs.miscellaneous_tab import MiscellaneousTab
from src.bot._states.out_of_combat._sub_states.banking._vault._tabs.resources_tab import ResourcesTab
from src.bot._states.out_of_combat._sub_states.banking.bank_data import Getter as BankDataGetter


class Vault:

    EQUIPMENT_TAB = EquipmentTab()
    MISCELLANEOUS_TAB = MiscellaneousTab()
    RESOURCES_TAB = ResourcesTab()

    @staticmethod
    def open():
        return Interfaces.BANK_VAULT.open()

    @staticmethod
    def close():
        return Interfaces.BANK_VAULT.close()

    @classmethod
    def deposit_all_tabs(cls):
        log.info("Depositing all tabs ... ")
        cls.EQUIPMENT_TAB.deposit_tab()
        cls.MISCELLANEOUS_TAB.deposit_tab()
        cls.RESOURCES_TAB.deposit_tab()
        log.info("Successfully deposited all tabs.")
