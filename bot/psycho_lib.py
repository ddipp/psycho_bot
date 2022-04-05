#!/usr/bin/env python

import random
from pathlib import Path


def get_decks_info(parent_dir, dirname):
    # get all subdirectory
    p = Path(parent_dir) / Path(dirname)
    decks = [x for x in p.iterdir() if x.is_dir()]
    # get info for each subdirectory
    info = {}
    for d in decks:
        f = d / 'INFO'
        if f.exists():
            info[f.open().readline().strip()] = d
        else:
            info[d.name] = d
    return info


def get_random_card(deckdir):
    p = Path(deckdir).glob('**/*')
    files = [x for x in p if x.is_file()]
    card = open(random.choice(files), 'rb')
    return card


if __name__ == "__main__":
    try:
        from productionconfig import DECK_DIR
    except ImportError:
        from config import DECK_DIR

    print(get_decks_info(DECK_DIR))
