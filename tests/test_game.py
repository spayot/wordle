import wordle as wd


def assert_game_evaluation(word, guess, shortform_expected_outcome: str):
    game = wd.WordleGame(word)
    outcome = game.evaluate_guess(guess)
    for guessed_letter, label in zip(outcome, shortform_expected_outcome):
        assert (
            guessed_letter.result.value == label
        ), f"expected {label} for letter {guessed_letter} in word: `{word}`"


def test_game_evaluation():
    assert_game_evaluation("crate", "fusil", "_____")
    assert_game_evaluation("crate", "trace", "OCCOC")
    assert_game_evaluation("crate", "treat", "OCOO_")
    assert_game_evaluation("crate", "treta", "_COCO")


def generate_game_sequence(target_word, guesses: list[str]):
    game = wd.WordleGame(target_word)
    for guess in guesses:
        game.record_player_guess(guess)
    return game


def test_game_sequence_unsolved():
    game = generate_game_sequence("crate", ["fusil", "treat"])
    assert not game.solved
    assert game.number_of_guesses == 2


def test_game_sequence_solved():
    game = generate_game_sequence("crate", ["fusil", "treat", "crate"])
    assert game.solved
    assert game.is_over
    assert game.number_of_guesses == 3


def test_game_sequence_out_of_guesses():
    game = generate_game_sequence("crate", ["fusil" for _ in range(6)])
    assert not game.solved
    assert game.is_over
    assert game.number_of_guesses == 6
