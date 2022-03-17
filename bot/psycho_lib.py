#!/usr/bin/env python

from pathlib import Path


def get_decks_info(dirname):
    # get all subdirectory
    p = Path(dirname)
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


if __name__ == "__main__":
    try:
        from productionconfig import DECK_DIR
    except ImportError:
        from config import DECK_DIR

    print(get_decks_info(DECK_DIR))
# def start(message):
#   if message.text == 'Фото':
#       photo = open('test/' + random.choice(os.listdir('test')), 'rb')
#       bot.send_photo(message.from_user.id, photo)
