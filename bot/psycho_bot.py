#!/usr/bin/env python
import os
import sys
import inspect
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from psycho_lib import get_decks_info  # noqa

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from productionconfig import TOKEN, REDISDB, DECK_DIR
except ImportError:
    from config import TOKEN, REDISDB, DECK_DIR

# Get decks directory
deck_dirs = get_decks_info(DECK_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = RedisStorage2(host='localhost', port=6379, db=REDISDB)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(regexp='привет')
async def vipcount(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for deck_name, deck_folder in deck_dirs.items():
        print(deck_name, deck_folder)
        keyboard.add(InlineKeyboardButton(text=deck_name, callback_data="select_folder:{0}".format(deck_name)))
    await message.reply("Шестое - запрашиваем контакт и геолокацию\nЭти две кнопки не зависят друг от друга", reply_markup=keyboard)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    msg = text(bold('Привет'),
               'Карта на сегодня',
               'Выбери колоду',
               deck_dirs,
               sep='\n')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(regexp='hello')
async def hell(message: types.Message):
    await message.reply("Hi!")


# @dp.message_handler(regexp='[0-9]+\.?[0-9]+? +\w+ +\D+')
@dp.message_handler(regexp='привет')
async def priv(message: types.Message):
    await message.answer("Привет привет")


if __name__ == '__main__':
    executor.start_polling(dp)  # , skip_updates=True)
