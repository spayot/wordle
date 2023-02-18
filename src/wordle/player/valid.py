# -------------------------------------- GUESS VALIDITY --------------------------------------


from wordle.game import Character, CharacterResult, GuessOutcome


def is_word_possible_given_guess_outcome(candidate_word: str, outcome: GuessOutcome):
    leftover = {i: char for i, char in enumerate(candidate_word.upper())}
    check, msg = _check_shares_correct_letters(leftover, outcome)
    if not check:
        return False, msg
    check, msg = _check_includes_oop_letters(leftover, outcome)
    if not check:
        return False, msg
    return _check_does_not_include_absent_letters(leftover, outcome)


def _check_shares_correct_letters(
    leftover: dict[str, Character], outcome: GuessOutcome
):
    for correct_gl in outcome.get(CharacterResult.CORRECT):
        if leftover[correct_gl.position] != correct_gl.letter:
            return False, f"Missing Correct Letter `{correct_gl.letter}`"
        leftover.pop(correct_gl.position)
    return True, "correct checks passed"


def _check_includes_oop_letters(leftover, outcome):
    for oop_gl in outcome.get(CharacterResult.OOP):
        if oop_gl.position in leftover:
            if leftover[oop_gl.position] == oop_gl.letter:
                return (
                    False,
                    f"OOP letter `{oop_gl.letter}` should have different position",
                )
        idx_oop = [i for i, char in leftover.items() if char == oop_gl.letter]
        if not idx_oop:
            return False, f"missing OOP letter `{oop_gl.letter}`"
        leftover.pop(idx_oop[0])
    return True, "oop checks passed"


def _check_does_not_include_absent_letters(leftover, outcome):
    for absent_gl in outcome.get(CharacterResult.ABSENT):
        if absent_gl.letter in leftover.values():
            return False, "`{absent_gl.letter}` should not be included"
    return True, "all checks passed"


def is_word_possible_given_guess_outcome(candidate_word: str, outcome: GuessOutcome):
    leftover = {i: char for i, char in enumerate(candidate_word)}
    check, msg = _check_shares_correct_letters(leftover, outcome)
    if not check:
        return False, msg
    check, msg = _check_includes_oop_letters(leftover, outcome)
    if not check:
        return False, msg
    return _check_does_not_include_absent_letters(leftover, outcome)
