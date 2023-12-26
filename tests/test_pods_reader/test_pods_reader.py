import os
import unittest
import re

from src.bot.states.out_of_combat.pods_reader.pods_reader import PodsReader
from src.utilities import load_image


class TestPodsReader(unittest.TestCase):

    IMAGE_DIR_PATH = "tests\\test_pods_reader\\images"
    POD_TOOLTIP_IMAGES = [
        {"name": "bank_vault_tooltip_1.png", "expected_text": "2258podsoutof21025"},
        {"name": "bank_vault_tooltip_2.png", "expected_text": "1043podsoutof21025"},
        {"name": "bank_vault_tooltip_3.png", "expected_text": "988podsoutof21025"},
        {"name": "bank_vault_tooltip_4.png", "expected_text": "427podsoutof21025"},
        {"name": "bank_vault_tooltip_5.png", "expected_text": "1043podsoutof21025"},
        {"name": "bank_vault_tooltip_6.png", "expected_text": "2254podsoutof21025"},
        {"name": "inventory_tooltip_1.png",  "expected_text": "1036podsoutof21025"}
    ]

    def test_read_tooltip_text(self):
        for image in self.POD_TOOLTIP_IMAGES:
            tooltip = load_image(self.IMAGE_DIR_PATH, image["name"])
            text = PodsReader.read_tooltip_text(tooltip)
            self.assertEqual(text, image["expected_text"])
