import pandas as pd
import plotly.express as px
from IPython.display import HTML, display

from wordle import game, player

COLORING = {"OOP": "#b89d02", "ABSENT": "black", "CORRECT": "#098710"}


def display_wordle_guess_outcome(results: game.GuessOutcome):
    html_string = '<font size="7" style="font-family:Monospace">'
    for gl in results.guessed_letters:
        html_string += f'<span style="background-color:{COLORING[gl.result.name]}">{gl.letter.upper()}</span>'

    display(HTML(html_string))


def generate_word_distrib(word, psm: player.PossibleSolutionsMap):
    distrib = (
        psm.map.groupby(word).apply(lambda x: list(x.index)).to_frame("possibilities")
    )
    distrib["pattern"] = distrib.index.map(game.decimal_to_ternary)
    distrib["n_words_matching"] = distrib.possibilities.apply(len)
    distrib["probability"] = distrib.n_words_matching / len(psm.map)
    distrib["possible_solutions"] = distrib.possibilities.apply(
        lambda x: pd.Series(x).sample(min(12, len(x))).sort_values().values
    )
    return distrib.sort_values("probability", ascending=False)


def plot_distrib(word: str, psm: player.PossibleSolutionsMap):
    distrib = generate_word_distrib(word, psm)
    fig = px.bar(
        distrib,
        x="pattern",
        y="probability",
        hover_data=["pattern", "n_words_matching", "probability", "possible_solutions"],
        template="plotly_dark",
        title=f"""
        Wordle outcome distribution with starting guess `{word}`
<br>prior entropy:       {psm.entropy:.2f}
<br>candidate expected information gain:  {psm.get_candidate_entropy(word):.2f}""",
    )
    fig.show()
