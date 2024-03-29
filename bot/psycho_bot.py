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
from aiogram.dispatcher import FSMContext

from psycho_lib import get_decks_info, get_random_card, how_much_is_available, add_card_to_day, how_long_to_wait  # noqa
from stats import PsychoStats, ActionStatus  # noqa

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from productionconfig import TOKEN, REDISDB, DECK_DIR, DEFAULT_CARDS_OF_DAY, ADMIN_ID
except ImportError:
    from config import TOKEN, REDISDB, DECK_DIR, DEFAULT_CARDS_OF_DAY, ADMIN_ID


# Stats component
stat = PsychoStats(REDISDB)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
storage = RedisStorage2(host='localhost', port=6379, db=REDISDB, pool_size=1000)
dp = Dispatcher(bot, storage=storage)

deck_cb = CallbackData('deck_cb', 'action', 'deck')


def get_decks_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    deck_dirs = list(get_decks_info(parent_dir, DECK_DIR).keys())
    deck_dirs = sorted(deck_dirs, key=len, reverse=True)

    while len(deck_dirs) > 0:
        this_btn = deck_dirs.pop()

        if len(this_btn) < 15 and len(deck_dirs) > 0 and len(deck_dirs[-1]) < 15:
            btn1 = InlineKeyboardButton(text=this_btn, callback_data=deck_cb.new(action='get_card', deck=this_btn))
            next_btn = deck_dirs.pop()
            btn2 = InlineKeyboardButton(text=next_btn, callback_data=deck_cb.new(action='get_card', deck=next_btn))
            keyboard.row(btn1, btn2)
        else:
            btn1 = InlineKeyboardButton(text=this_btn, callback_data=deck_cb.new(action='get_card', deck=this_btn))
            keyboard.row(btn1)
    return keyboard


@dp.message_handler(regexp='хочу карту')
@dp.message_handler(commands=['card'])
async def vipcount(message: types.Message, state: FSMContext):
    c = await how_much_is_available(state, DEFAULT_CARDS_OF_DAY)
    if c > 0 or message.from_user.id in ADMIN_ID:
        keyboard = get_decks_keyboard()
        await message.answer("Из какой колоды вытягиваем карту?", reply_markup=keyboard)
        await stat.add_action(message.from_user.id, ActionStatus.request_card, 1)
    else:
        next_through = await how_long_to_wait(state, DEFAULT_CARDS_OF_DAY)
        await message.answer(
            'Извините, я могу дать только три карты в 24 часа, следующая через {0}'.format(next_through),
            parse_mode=ParseMode.MARKDOWN
        )
        await stat.add_action(message.from_user.id, ActionStatus.request_card, 0)


@dp.callback_query_handler(deck_cb.filter(action='get_card'))
async def get_card_cb_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    c = await how_much_is_available(state, DEFAULT_CARDS_OF_DAY)
    if c > 0 or query.from_user.id in ADMIN_ID:
        deck_dirs = get_decks_info(parent_dir, DECK_DIR)
        card = get_random_card(deck_dirs[callback_data['deck']])
        await add_card_to_day(state)
        await bot.send_photo(chat_id=query.from_user.id, photo=card)
        await bot.edit_message_text('{0}'.format(callback_data['deck']),
                                    query.from_user.id,
                                    query.message.message_id)
        await stat.add_action(query.from_user.id, ActionStatus.send_card, 1)
    else:
        next_through = await how_long_to_wait(state, DEFAULT_CARDS_OF_DAY)
        await bot.edit_message_text(
            'Извините, я могу дать только {1} карты в 24 часа, следующая через {0}'.format(next_through, DEFAULT_CARDS_OF_DAY),
            query.from_user.id,
            query.message.message_id)
        await stat.add_action(query.from_user.id, ActionStatus.send_card, 0)


@dp.message_handler(commands=['rules'])
async def rules(message: types.Message):
    msg = text(bold('Правила\n'),
               'Вы можете получить не более трех карт в день\n',
               sep='')
    await stat.add_action(message.from_user.id, ActionStatus.rules, 1)
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
    await stat.add_action(message.from_user.id, ActionStatus.help, 1)
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    msg = text(bold('Привет\n'),
               'Метафорические карты - это психологический инструмент.\n',
               'Если ты еще не знаешь как им пользоваться, посмотри инструкцию в меню (или нажмите /help).\n',
               'Формулируй запрос, пиши - ', bold('"хочу карту",'), '(или нажмите в меню /card)  и выбирай колоду.',
               sep='')
    await stat.add_action(message.from_user.id, ActionStatus.start, 1)
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN)


async def setup_bot_commands(dp):
    bot_commands = [
        types.BotCommand(command="/start", description="Начало"),
        types.BotCommand(command="/help", description="Инструкция"),
        types.BotCommand(command="/rules", description="Правила"),
        types.BotCommand(command="/card", description="Хочу карту")
    ]
    await dp.bot.set_my_commands(bot_commands)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=setup_bot_commands)
