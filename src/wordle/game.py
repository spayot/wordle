from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

_powers_of_three = (3 ** np.arange(5)).astype(np.uint8)
Character = str


class CharacterResult(Enum):
    ABSENT = 0
    OOP = 1
    CORRECT = 2


@dataclass
class GuessedLetter:
    position: int
    letter: Character
    result: CharacterResult


class GameOverException(Exception):
    pass


class GuessOutcome:
    def __init__(self, guessed_letters: list[GuessedLetter]):
        self.guessed_letters = guessed_letters
        self.guess_word = "".join([gl.letter for gl in guessed_letters]).upper()
        ternary = "".join([str(gl.result.value) for gl in guessed_letters])
        self.ternary = ternary
        # self.powers_of_three = (3 ** np.arange(len(guessed_letters))).astype(np.uint8)
        self.uint8 = self._to_uint8(ternary)

    def __getitem__(self, i: int):
        return self.guessed_letters[i]

    def __iter__(self):
        return iter(self.guessed_letters)

    def get(self, char_result) -> dict:
        return [gl for gl in self.guessed_letters if gl.result == char_result]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.guess_word}, {self.ternary}, uint8={self.uint8})"

    @staticmethod
    def _to_uint8(ternary: str):
        return np.dot(
            [int(x) for x in ternary],
            _powers_of_three,
        )

    @classmethod
    def from_uint8(cls, guess_word: str, uint8: int) -> GuessOutcome:
        ternary = decimal_to_ternary(uint8, len(guess_word))
        guessed_letters = [
            GuessedLetter(pos, letter, CharacterResult(int(r)))
            for pos, (letter, r) in enumerate(zip(guess_word, ternary))
        ]
        return cls(guessed_letters)


def decimal_to_ternary(uint8: int, word_length: int = 5) -> str:
    """converts a uint8 representation of a guess outcome into a ternary representation."""
    if uint8 == 0:
        return "0" * word_length
    ternary = ""
    while uint8 > 0:
        remainder = uint8 % 3
        ternary = ternary + str(remainder)
        uint8 //= 3
    return ternary.ljust(word_length, "0")


def ternary_to_decimal(ternary: str):
    ternary_arr = np.array([int(digit) for digit in ternary])
    decimal = np.sum(ternary_arr[::-1] * _powers_of_three)
    return decimal


@dataclass
class WordleGame:
    target_word: str = None
    max_guesses: int = 6
    number_of_guesses: int = 0
    guesses_so_far: list[GuessOutcome] = field(default_factory=list, repr=False)
    is_over: bool = False
    solved: bool = False

    def __post_init__(self):
        self.target_word = self.target_word.upper()

        if not self.target_word:
            self.target_word = self.random_choose_target_words()

    def random_choose_target_words(self) -> str:
        return "tests"

    def evaluate_guess(self, guess_word: str):
        guess_word = guess_word.upper()
        guessed_letter_list = _find_correct_letters(self.target_word, guess_word)
        leftover_target = _remove_correct(self.target_word, guessed_letter_list)
        leftover_guess = _remove_correct(guess_word, guessed_letter_list)

        for i, char in leftover_guess.items():
            if char not in leftover_target.values():
                guessed_letter_list.append(
                    GuessedLetter(i, char, CharacterResult.ABSENT)
                )
            else:
                guessed_letter_list.append(GuessedLetter(i, char, CharacterResult.OOP))
                _remove_first_dict_item_with_value(leftover_target, char)

        return _sort_and_convert_to_guess_outcome(guessed_letter_list)

    def successful(self, guess_outcome: GuessOutcome):
        return self.target_word == guess_outcome.guess_word

    def record_player_guess(self, guess_word: str) -> GuessOutcome:
        if self.is_over:
            raise GameOverException(f"this game is already over: \n{self}")

        guess_outcome = self.evaluate_guess(guess_word)
        self.guesses_so_far.append(guess_outcome)
        self.number_of_guesses += 1

        if self.successful(guess_outcome):
            self.is_over = True
            self.solved = True

        if self.number_of_guesses == 6:
            self.is_over = True

        return guess_outcome

    @property
    def score(self) -> int:
        if not self.is_over:
            return None
        else:
            return 6 - self.number_of_guesses + int(self.solved)


def _find_correct_letters(target_word: str, guess_word: str) -> list[GuessedLetter]:
    return [
        GuessedLetter(position, guess_char, CharacterResult.CORRECT)
        for position, (guess_char, word_char) in enumerate(zip(target_word, guess_word))
        if guess_char == word_char
    ]


def _remove_correct(
    word: str, correct_letters: list[GuessedLetter]
) -> dict[int, Character]:
    correct_positions = [letter.position for letter in correct_letters]
    return {i: char for i, char in enumerate(word) if i not in correct_positions}


def _remove_first_dict_item_with_value(
    leftover_target: dict[int, Character], char: Character
) -> None:
    if char not in leftover_target.values():
        return leftover_target

    idx_to_remove = [i for i, c in leftover_target.items() if c == char][0]
    _ = leftover_target.pop(idx_to_remove)


def _sort_and_convert_to_guess_outcome(
    guessed_letters: list[GuessedLetter],
) -> GuessOutcome:
    sorted_guessed_letters = sorted(guessed_letters, key=lambda x: x.position)
    return GuessOutcome(sorted_guessed_letters)
