from enum import Enum


class Status(Enum):

    # VaultActions
    TAB_FAILED_TO_OPEN = "failed_to_open_tab"
    TAB_NO_ITEMS_TO_DEPOSIT = "no_items_to_deposit"
    TAB_FINISHED_DEPOSITING_ITEMS = "finished_depositing_items"
    TAB_FAILED_TO_DEPOSIT_ITEMS = "failed_to_deposit_items"
    FAILED_TO_DEPOSIT_ALL_TABS = "tab_depositing_failed"
    SUCCESSFULLY_DEPOSITED_ALL_TABS = "successfully_deposited_all_tabs"
