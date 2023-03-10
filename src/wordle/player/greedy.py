from wordle import game, player
from wordle.player import map


class GreedyPlayer:
    def __init__(self, starting_psm: map.PossibleSolutionsMap):
        self._starting_psm = starting_psm
        self.psm = starting_psm

    def make_next_guess(self, game: game.WordleGame) -> str:
        # select candidate guess with highest entropy
        if len(self.psm.possible_solutions) <= 2:
            return self.psm.possible_solutions.index[0]

        return player.get_all_candidate_entropies(self.psm).index[0]

    def update(self, guess_outcome: game.GuessOutcome) -> None:
        self.psm = self.psm.filter_based_on_guess_outcome(guess_outcome)

    def start_new_game(self) -> None:
        self.psm = self._starting_psm
