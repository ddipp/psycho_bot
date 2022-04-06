#!/usr/bin/env python
import os
import sys
import inspect
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from psycho_lib import get_decks_info, get_random_card  # noqa

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from productionconfig import TOKEN, REDISDB, DECK_DIR
except ImportError:
    from config import TOKEN, REDISDB, DECK_DIR

# Get decks directory
deck_dirs = get_decks_info(parent_dir, DECK_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = RedisStorage2(host='localhost', port=6379, db=REDISDB)
dp = Dispatcher(bot, storage=storage)

deck_cb = CallbackData('deck_cb', 'action', 'deck')


def get_decks_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    for deck_name, deck_folder in deck_dirs.items():
        keyboard.add(InlineKeyboardButton(text=deck_name, callback_data=deck_cb.new(action='get_card', deck=deck_name)))
    return keyboard


@dp.message_handler(regexp='хочу карту')
async def vipcount(message: types.Message):
    keyboard = get_decks_keyboard()
    await message.answer("Из какой колоды вытягиваем карту?", reply_markup=keyboard)


@dp.callback_query_handler(deck_cb.filter(action='get_card'))
async def get_card_cb_handler(query: types.CallbackQuery, callback_data: dict):
    # logging.info(callback_data)
    card = get_random_card(deck_dirs[callback_data['deck']])
    await bot.send_photo(chat_id=query.from_user.id, photo=card)
    await bot.edit_message_text('{0}'.format(callback_data['deck']),
                                query.from_user.id,
                                query.message.message_id)


@dp.message_handler(commands=['rules'])
async def rules(message: types.Message):
    msg = text(bold('Правила\n'),
               'Вы можете получить не более трех карт в день\n',
               sep='')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    msg = text(bold('Как формулировать запрос\n'),
               '1. Он должен подразумевать открытый ответ\n',
               '2. Запрос не должен запрашивать даты или сроки\n',
               '3. Вопрос должен быть про Вас или Ваше состояние\n\n',
               bold('Примерные запросы:\n'),
               '- Что мне мешает (построить отношения, увеличить доход и т.д.)\n',
               '- Что мне поможет (построить отношения, увеличить доход и т.д.)\n',
               'Возможны и другие формулировки, только помните что это не гадание\n\n',
               bold('Как трактовать карты:\n'),
               '1. Не стоит сразу искать в изображении себя\n',
               '2. Почувствуйте какие эмоции и ассоциации вызывает карта\n',
               '3. Смотрите на рисунок как на иллюстрацию в книге и пофантазируйте к какой истории эта иллюстрация\n',
               '4. Именно в этой истории будет подсказка на Ваш запрос или напутствие на день\n',
               sep='')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    msg = text(bold('Привет\n'),
               'Метафорические карты - это психологический инструмент.\n',
               'Если ты еще не знаешь как им пользоваться, посмотри инструкцию в меню (или нажмите /help).\n',
               'Формулируй запрос, пиши - ', bold('"хочу карту",'), '  и выбирай колоду.',
               sep='')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp)  # , skip_updates=True)
