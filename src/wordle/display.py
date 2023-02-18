from IPython.display import HTML, display

from wordle.game import GuessOutcome

COLORING = {"OOP": "#b89d02", "ABSENT": "black", "CORRECT": "#098710"}


def display_wordle_guess_outcome(results: GuessOutcome):
    html_string = '<font size="7" style="font-family:Monospace">'
    for gl in results.guessed_letters:
        html_string += f'<span style="background-color:{COLORING[gl.result.name]}">{gl.letter.upper()}</span>'

    display(HTML(html_string))
