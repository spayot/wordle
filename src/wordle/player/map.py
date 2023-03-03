from __future__ import annotations

import functools
import pickle
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import wordle as wd


@dataclass
class PossibleSolutionsMap:
    def __init__(self, possible_solutions: dict[str, float], allowed_words: list[str]):
        """
        attributes:
            possible_solutions: stores a dictionary `word / weight` where the weight allows to
                provide likelihood for a word to be the solution, typically based on how frequently
                it is used in English.
            allowed_words: the list of words that can be used to make a guess (includes but not limited
                to possible solutions)
            map: a pandas DataFrame storing the shortform of the guess outcome if trying a guess | given
                an actual solution. the DataFrame will have the keys of `possible_solutions` as index and
                `allowed_words` as columns. Values will be shorform (e.g. "CO__C", cf. `game.GuessOutcome`)
            entropy: evaluates the amount of remaining uncertainty given the remaining possible_solutions
        """
        self.possible_solutions = pd.Series(possible_solutions)
        self.n_solutions: int = len(possible_solutions)
        self.allowed_words = allowed_words
        self.n_allowed = len(allowed_words)

    def build_map(self) -> dict[defaultdict(dict)]:
        """"""
        mapping = defaultdict(dict)
        for solution in self.possible_solutions.index:
            game = wd.WordleGame(solution)
            for guess_word in self.allowed_words:
                guess_outcome = game.evaluate_guess(guess_word)
                mapping[solution][guess_word] = guess_outcome.shortform

        self.map = pd.DataFrame.from_dict(mapping, orient="index")

    @classmethod
    def from_map(cls, map: pd.DataFrame, possible_solutions: dict[str, float]):
        assert set(possible_solutions.keys()) == set(map.index)
        psm = cls(possible_solutions, allowed_words=map.columns)
        psm.map = map
        return psm

    def filter_based_on_guess_outcome(
        self, guess_outcome: wd.game.GuessOutcome
    ) -> PossibleSolutionsMap:
        map = self.map.query(
            f"{guess_outcome.guess_word.lower()}=='{guess_outcome.shortform}'"
        )
        return PossibleSolutionsMap.from_map(
            map=map, possible_solutions=self.possible_solutions[map.index]
        )

    @property
    def entropy(self) -> float:
        """measures the remaining level of uncertainty given the possible solutions left.

        Note: only depends on possible solutions"""
        return self._words_freq_series_to_entropy(self.possible_solutions)

    def get_candidate_entropy(
        self: PossibleSolutionsMap, candidate_guess: str
    ) -> float:
        """calculates entropy for a given `candidate_guess`"""
        """expected bits of information to be gained from using this guess,
        given the possible solutions left."""
        grouped_words = self.possible_solutions.groupby(
            self.map.loc[:, candidate_guess]
        ).sum()
        return self._words_freq_series_to_entropy(grouped_words)

    def _words_freq_series_to_entropy(self, wf: pd.Series) -> float:
        # turn weights into probabilities
        p = wf / self.possible_solutions.sum()
        # apply entropy formula
        return -(p * np.log2(p)).sum()

    def to_pickle(self, path: Path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle(cls, path: Path):
        with open(path, "rb") as f:
            psm = pickle.load(f)

        return psm

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(n_solutions={self.n_solutions},n_allowed={self.n_allowed},entropy={self.entropy:.2f})"

    def __hash__(self):
        """implementing a hashing strategy allows to use caching on functions calling
        a
        """
        return hash(("".join(self.possible_solutions.keys())))


def get_candidate_entropy(psm: PossibleSolutionsMap, candidate_word: str) -> float:
    grouped_words = psm.possible_solutions.groupby(psm.map.loc[:, candidate_word]).sum()
    return psm._words_freq_series_to_entropy(grouped_words)


@functools.lru_cache(maxsize=1_000)
def get_all_candidate_entropies(psm: PossibleSolutionsMap) -> pd.Series:
    return pd.Series(
        {word: psm.get_candidate_entropy(word) for word in psm.map.columns}
    ).sort_values(ascending=False)


def print_candidate_entropies(entropies: pd.Series) -> None:
    print(entropies.head(8).to_string(float_format="{:.3f}".format))
