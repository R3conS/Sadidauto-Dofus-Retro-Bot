from enum import Enum


class Status(Enum):

    # VaultActions
    TAB_FAILED_TO_OPEN = "failed_to_open_tab"
    TAB_NO_ITEMS_TO_DEPOSIT = "no_items_to_deposit"
    TAB_FINISHED_DEPOSITING_ITEMS = "finished_depositing_items"
    TAB_FAILED_TO_DEPOSIT_ITEMS = "failed_to_deposit_items"
    FAILED_TO_DEPOSIT_ALL_TABS = "tab_depositing_failed"
    SUCCESSFULLY_DEPOSITED_ALL_TABS = "successfully_deposited_all_tabs"

    # Banker
    SUCCESSFULLY_RECALLED = "successfully_recalled"
    SUCCESSFULLY_ENTERED_BANK = "successfully_entered_bank"
    SUCCESSFULLY_OPENED_BANK_VAULT = "successfully_opened_bank_vault"
    SUCCESSFULLY_LEFT_BANK = "successfully_left_bank"
    FAILED_TO_DETECT_LOADING_SCREEN_AFTER_RECALL = "failed_to_detect_loading_screen_after_recall"
    FAILED_TO_DETECT_LOADING_SCREEN_AFTER_CHANGE_MAP = "failed_to_detect_loading_screen_after_change_map"
    FAILED_TO_RECALL = "failed_to_recall"
    FAILED_TO_ENTER_BANK = "failed_to_enter_bank"
    FAILED_TO_LEAVE_BANK = "failed_to_leave_bank"
    FAILED_TO_OPEN_BANK_VAULT = "failed_to_open_bank_vault"
    FAILED_TO_CLOSE_BANK_VAULT = "failed_to_close_bank_vault"
    FAILED_TO_DETECT_BANKER_NPC = "failed_to_detect_banker_npc"
    FAILED_TO_OPEN_BANKER_DIALOGUE = "failed_to_open_banker_dialogue"
    CHAR_DOESNT_HAVE_RECALL_POTION = "char_doesnt_have_recall_potion"
    NO_NEED_TO_RECALL = "no_need_to_recall"
    ARRIVED_AT_ASTRUB_BANK_MAP = "arrived_at_astrub_bank_map"
