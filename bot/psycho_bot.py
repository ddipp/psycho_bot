#!/usr/bin/env python
import os
import sys
import inspect
import logging

from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from productionconfig import TOKEN, REDISDB, DECK_DIR
except ImportError:
    from config import TOKEN, REDISDB, DECK_DIR

print(list(Path(DECK_DIR).glob('*')))

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = RedisStorage2(host='localhost', port=6379, db=REDISDB)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    msg = text(bold('Привет'),
               'Можно выбрать колоду',
               'можно не выбирать',
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
