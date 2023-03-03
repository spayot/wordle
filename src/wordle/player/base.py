from typing import Protocol

from wordle.display import display_wordle_guess_outcome
from wordle.game import GuessOutcome, WordleGame


class Player(Protocol):
    def make_next_guess(self, game: WordleGame) -> str:
        ...

    def update(self, guess_outcome: GuessOutcome) -> None:
        ...


def play_game(player: Player, game: WordleGame, quiet: bool = False) -> WordleGame:
    while not game.is_over:
        guess = player.make_next_guess(game)
        outcome = game.record_player_guess(guess)
        player.update(outcome)
        if not quiet:
            display_wordle_guess_outcome(outcome)

    return game
