import numpy as np

from src.utilities.general import load_image_full_path
from src.utilities.ocr.ocr import OCR


class Reader:

    MONSTER_NAMES = ["Boar", "Mush Mush", "Prespic", "Moskito", "Miliboowolf"]

    def __init__(self, precise_tooltip_image: np.ndarray | str):
        if isinstance(precise_tooltip_image, str):
            self._precise_tooltip_image = load_image_full_path(precise_tooltip_image)
        else:
            self._precise_tooltip_image = precise_tooltip_image
        text = self._get_tooltip_text()
        words = self._combine_text_into_words(text)
        self.monster_counts = self._count_monsters(words)

    def _get_tooltip_text(self):
        image = OCR.convert_to_grayscale(self._precise_tooltip_image)
        image = OCR.binarize_image(image, 155)
        image = OCR.invert_image(image)
        return OCR.get_text_from_image(image)

    @classmethod
    def _remove_forbidden_characters(cls, text: str):
        return text.translate(str.maketrans("", "", "".join(cls._get_forbidden_characters())))

    @staticmethod
    def _combine_text_into_words(tooltip_text):
        words = []
        word = ""
        for char in tooltip_text:
            if char.isspace():
                if word:
                    words.append(word)
                    word = ""
            else:
                word += char
        if word:
            words.append(word)
        return words

    @staticmethod
    def _get_forbidden_characters():
        return [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
            ".", ",", ":", ";", "!", "?", "(", ")", "[", "]", "{", "}"
        ]

    @staticmethod
    def _does_word_have_matching_subsequence(full_word: str, subsequence: str, min_length_to_match=4):
        word_len = len(full_word)
        subsequence_len = len(subsequence)
        if word_len < min_length_to_match or subsequence_len < min_length_to_match:
            return False
        for i in range(word_len - min_length_to_match + 1):
            if full_word[i:i+min_length_to_match] in subsequence:
                return True
        return False

    @classmethod
    def _is_monster(cls, word: str):
        for monster_name in cls.MONSTER_NAMES:
            if cls._does_word_have_matching_subsequence(monster_name, word):
                return True
        return False
    
    @classmethod
    def _get_full_monster_name(cls, word: str):
        for monster_name in cls.MONSTER_NAMES:
            if cls._does_word_have_matching_subsequence(monster_name, word):
                return monster_name
        return None

    @classmethod
    def _count_monsters(cls, tooltip_words):
        monsters = {}
        for word in tooltip_words:
            if cls._is_monster(word):
                full_name = cls._get_full_monster_name(word)
                if full_name in monsters:
                    monsters[full_name] += 1
                else:
                    monsters[full_name] = 1
        return monsters


if __name__ == "__main__":
    reader = Reader("test.png")
