from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import partial
from multiprocessing.pool import ThreadPool as Pool
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from wordle import game as game_module
from wordle import load
from wordle import player as player_module


@dataclass
class EvalResults:
    scores: dict[str, int] = field(default_factory=dict, repr=False)

    def value_counts(self):
        return (
            pd.Series(self.scores)
            .value_counts()
            .reindex(range(7), fill_value=0)
            .sort_index()
            .rename("counts")
        )

    def __setitem__(self, key, value):
        self.scores[key] = value

    @property
    def eval_size(self):
        return len(self.scores)

    @property
    def avg_score(self):
        return pd.Series(self.scores, dtype=float).mean()

    @property
    def success_rate(self):
        return (pd.Series(self.scores) > 0).mean()

    def distribution(self) -> list[int]:
        return self.value_counts().values

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.eval_size:,}, avg_score={self.avg_score:.2f}, dist={self.distribution()}, success_rate={self.success_rate:.1%})"

    def to_json(self, path: Path) -> None:
        with open(path, "w") as fp:
            json.dump(self.scores, fp, indent=4)

    @classmethod
    def from_json(cls, path: Path) -> EvalResults:
        with open(path, "r") as fp:
            scores = json.load(fp)
        return cls(scores)

    def barplot(self, title: str):
        fig = px.bar(
            self.value_counts(),
            template="plotly_dark",
            title=f"{title}<br>avg. score: {self.avg_score:.2f}<br>success rate: {self.success_rate:.0%}",
            y="counts",
            labels={
                "index": "game score (points)",
                "counts": "number of evaluated games",
            },
        )
        fig.update_yaxes({"range": [0, len(self.scores)]})
        fig.show()
        return fig


def play_eval_game(
    eval_word: str, player: player_module.Player
) -> game_module.WordleGame:
    game = game_module.WordleGame(eval_word)
    game = player_module.play_game(player, game, quiet=True)
    return eval_word, game.score


def eval_player(
    eval_words_list: list[str],
    player: player_module.Player,
    pool_size: int = 1,
) -> EvalResults:

    get_score = partial(play_eval_game, player=player)
    scores = EvalResults()

    with Pool(pool_size) as p:
        for word, score in p.imap_unordered(get_score, eval_words_list):
            scores[word] = score
            print(scores, end="\r")

    print(scores)
    return scores


def run_eval_from_config(config) -> tuple[EvalResults, go.Figure]:

    player_module.get_all_candidate_entropies.cache_clear()
    eval_words_list = load.load_words_as_list(config["path_to_eval_words_list"])

    results = eval_player(eval_words_list, config["player"], pool_size=1)

    # save results
    results.to_json(config["path_to_json_output"])
    print(f"results saved in `{config['path_to_json_output']}`")

    fig = results.barplot(title=config["fig_title"])
    fig.write_image(config["fig_name"])

    return results, fig
