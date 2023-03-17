import functools
from typing import Any

import pandas as pd
from tqdm.notebook import tqdm

from wordle import game
from wordle.player import base, map
from wordle.player.base import Player
from wordle.player.map import PossibleSolutionsMap, get_all_candidate_entropies


class TwoStepPlayer(Player):
    def __init__(
        self,
        starting_psm: PossibleSolutionsMap,
        starting_guess: str = None,
        max_first_guesses: int = None,
    ):
        self.starting_psm = starting_psm
        self.starting_guess = starting_guess
        self.max_first_guesses = (
            max_first_guesses if max_first_guesses else starting_psm.n_allowed
        )

        self.current_psm = starting_psm

    def start_new_game(self) -> None:
        self.current_psm = self.starting_psm

    def update(self, guess_outcome: game.GuessOutcome) -> None:
        self.current_psm = self.current_psm.filter_based_on_guess_outcome(guess_outcome)

        self.next_guess = guess_outcome.guess_word

    def make_next_guess(self, game: game.WordleGame) -> str:
        if (len(game.guesses_so_far) == 0) & (self.starting_guess is not None):
            return self.starting_guess

        if len(self.current_psm.possible_solutions) <= 2:
            return self.current_psm.possible_solutions.index[0]

        return self.find_guess_with_max_two_step_entropy()

    @functools.lru_cache(maxsize=300)
    def find_guess_with_max_two_step_entropy(self) -> str:
        return self.calculate_two_step_entropies().index[0]

    def calculate_two_step_entropies(self, show_tqdm: bool = False) -> pd.DataFrame:
        top_guesses_step_1 = get_all_candidate_entropies(self.current_psm).iloc[
            : self.max_first_guesses
        ]
        # get step 2 entropies for top guesses
        return self._calculate_step_two_entropies_for_guess_list(
            top_guesses_step_1, show_tqdm=show_tqdm
        )

    def _calculate_step_two_entropies_for_guess_list(
        self, top_guesses_step_1: pd.Series, show_tqdm: bool = False
    ) -> pd.DataFrame:
        step_two_entropies = []
        iterator = top_guesses_step_1.items()
        if show_tqdm:
            iterator = tqdm(iterator, total=len(top_guesses_step_1))

        for candidate_guess, entropy_step_1 in iterator:
            step_two_entropies.append(
                self._get_two_steps_entropies(candidate_guess, entropy_step_1)
            )
        return self._format_two_steps_entropies_to_df(step_two_entropies)

    def _get_two_steps_entropies(
        self, candidate_guess: str, entropy_step_1: float
    ) -> dict[str, Any]:
        entropy_step_2 = self.get_step_two_entropy(candidate_guess, quiet=True)
        return {
            "guess_word": candidate_guess,
            "entropy_step_1": entropy_step_1,
            "entropy_step_2": entropy_step_2,
            "entropy_total": entropy_step_1 + entropy_step_2,
        }

    def _format_two_steps_entropies_to_df(
        self, two_step_entropies: list[dict]
    ) -> pd.DataFrame:
        return (
            pd.DataFrame(two_step_entropies)
            .set_index("guess_word")
            .sort_values(["entropy_total", "entropy_step_1"], ascending=[False, False])
        )

    def get_step_two_entropy(self, first_guess: str, quiet: bool = False) -> float:
        """returns the entropy of the first guess, as well as the weighted average
        of the entropy of the best next guess (for each possible outcome)."""

        outcome_probabilities = self._get_outcome_probabilities(first_guess)
        entropy_step_2 = self._get_next_step_entropy(
            first_guess, outcome_probabilities, quiet
        )

        return entropy_step_2

    def _get_next_step_entropy(
        self, first_guess: str, outcome_probabilities: pd.Series, quiet: bool
    ) -> float:
        entropy_step_2 = 0
        iterator = outcome_probabilities.items()
        if not quiet:
            iterator = tqdm(iterator, total=len(outcome_probabilities))

        for uint8, prob in iterator:
            (
                best_next_word,
                next_step_entropy,
            ) = self._get_next_step_entropy_given_outcome(first_guess, uint8)
            entropy_step_2 += prob * next_step_entropy

        return entropy_step_2

    def _get_outcome_probabilities(self, first_guess) -> pd.Series:
        """counts how often each outcome can occur given the possible solutions defined in psm"""
        outcome_counts = self.current_psm.map[first_guess].value_counts()
        return outcome_counts / outcome_counts.sum()

    def _get_next_step_entropy_given_outcome(self, first_guess, uint8):
        outcome = game.GuessOutcome.from_uint8(first_guess, uint8)
        psm_step2 = self.current_psm.filter_based_on_guess_outcome(outcome)

        best_next_word, next_step_entropy = next(
            get_all_candidate_entropies(psm_step2).items()
        )
        return best_next_word, next_step_entropy

    def __hash__(self):
        """implementing a hashing strategy allows to use caching on functions calling"""
        return hash(self.current_psm)


@functools.lru_cache(maxsize=300)
def find_guess_with_max_two_step_entropy_with_caching(tsp: TwoStepPlayer) -> str:
    """unfortunately, caching is not instance specific"""
    return tsp.calculate_two_step_entropies().index[0]
