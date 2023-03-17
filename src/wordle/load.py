from pathlib import Path


def load_words_as_list(path: Path) -> list[str]:
    with open(path, "r") as f:
        return [word.strip() for word in f.readlines()]


def load_words_as_dict(path: Path) -> dict[str, float]:
    words = load_words_as_list(path)
    return {word: 1.0 for word in words}
