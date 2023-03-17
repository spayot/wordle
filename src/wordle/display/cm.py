import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import figure, patches
from sklearn import metrics

from wordle import eval

SETTINGS = {
    "style": "dark_background",
    "gridlines": {
        "color": "white",
        "alpha": 0.4,
    },
    "title": {"c": "white"},
    "cm_im_kw": {"vmin": -2000, "alpha": 0.8},
    "diagonal": {"facecolor": "grey", "alpha": 0.1},
}
plt.style.use(SETTINGS["style"])


def remove_value_from_plot_annotations(ax, value: str = "0"):
    for child in ax.get_children():
        if isinstance(child, plt.Text):
            if child.get_text() == value:
                child.set_text("")
            child.set_color((1, 1, 1, 1))


def set_grid_lines(ax):

    args = ([0.5 + n for n in range(6)], -0.5, 6.5)

    ax.hlines(*args, **SETTINGS["gridlines"])
    ax.vlines(*args, **SETTINGS["gridlines"])


def create_confusion_matrix(scores: pd.DataFrame) -> np.ndarray:
    cm = metrics.confusion_matrix(scores.res1, scores.res2, labels=list(range(7)))

    # turn 0s into np.nan to black out those images
    cm = cm.astype(np.float32)
    cm[cm == 0] = np.nan

    return cm


def add_unit_square(ax, center1, center2, *args, **kwargs):
    ax.add_patch(patches.Rectangle((center1 - 0.5, center2 - 0.5), 1, 1, zorder=1))


def display_diagonal(ax, n=7):
    for i in range(n):
        add_unit_square(ax, i, i, **SETTINGS["diagonal"])


def plot_confusion_matrix(
    results1: eval.EvalResults,
    results2: eval.EvalResults,
    label1: str,
    label2: str,
) -> figure.Figure:
    """plots a confusion matrix comparing the scores side by side of each
    wordle player.

    Assumption: results1 and results2 have been evaluated on the same
    """

    assert set(results1.scores.keys()) == set(
        results2.scores.keys()
    ), "results1 and results2 should be based on the same test set"

    fig, ax = plt.subplots()
    scores = pd.DataFrame({"res1": results1.scores, "res2": results2.scores})
    cm = create_confusion_matrix(scores)

    display_diagonal(ax)

    disp = metrics.ConfusionMatrixDisplay(cm)
    im_kw = {"zorder": 2}
    im_kw.update(SETTINGS["cm_im_kw"])

    disp.plot(
        colorbar=False,
        cmap="Purples",
        values_format=".0f",
        ax=ax,
        im_kw=im_kw,
    )

    remove_value_from_plot_annotations(ax, "nan")

    ax.set_title(
        f"test set scores comparison: {label1} vs {label2}", **SETTINGS["title"]
    )
    ax.set_xlabel(f"{label2} scores (avg: {results2.avg_score:.3f})")
    ax.set_ylabel(f"{label1} scores (avg: {results1.avg_score:.3f})")
    ax.tick_params(axis="both", which="both", length=0)
    set_grid_lines(ax)

    return fig
