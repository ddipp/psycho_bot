#!/usr/bin/env python

from pathlib import Path


def get_decks_info(dirname):
    # get all subdirectory
    p = Path(dirname)
    decks = [x for x in p.iterdir() if x.is_dir()]
    return decks


if __name__ == "__main__":
    try:
        from productionconfig import DECK_DIR
    except ImportError:
        from config import DECK_DIR

    print(get_decks_info(DECK_DIR))
