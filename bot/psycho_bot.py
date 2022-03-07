#!/usr/bin/env python
import os
import sys
import inspect
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from productionconfig import TOKEN, REDISDB
except ImportError:
    from config import TOKEN, REDISDB

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = RedisStorage2(host='localhost', port=6379, db=REDISDB)
dp = Dispatcher(bot, storage=storage)
