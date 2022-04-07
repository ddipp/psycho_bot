#!/usr/bin/env python

import random
import time
from pathlib import Path

period = 60 * 60 * 24


async def how_long_to_wait(state, cards_of_day):
    if await how_much_is_available(state, cards_of_day) > 0:
        return "Да хоть прямо сейчас!"
    else:
        current_time = int(time.time())
        data = await state.get_data()
        if 'cards' not in data.keys():
            data['cards'] = {}
        cards = data['cards']
        d = current_time - int(next(iter(cards)))
        return "{0}".format(time.strftime("%H:%M:%S", time.gmtime(period - d)))


async def add_card_to_day(state):
    current_time = int(time.time())
    data = await state.get_data()
    if 'cards' not in data.keys():
        data['cards'] = {}

    cards = data['cards']
    cards[current_time] = 1
    await state.update_data(cards=cards)


async def how_much_is_available(state, cards_of_day):
    current_time = int(time.time())
    data = await state.get_data()
    if 'cards' not in data.keys():
        data['cards'] = {}

    cards = data['cards']

    # проверяем выданные карты
    for key in sorted(cards):
        if current_time - int(key) > period:
            del cards[key]

    # Снова проверяем сколько осталось
    if len(cards) < cards_of_day:
        print('Можно выдать')
    print(cards)
    await state.update_data(cards=cards)
    return cards_of_day - len(cards)


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
