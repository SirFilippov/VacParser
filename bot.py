import asyncio
import random
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import (KeyboardButton,
                           ReplyKeyboardMarkup,
                           Message)

from parser import Parser
from mongo_db import DBManager
from settings import TOKEN, ADMIN_ID

# todo Добавить кнопку статуса работы парсера
# todo Добавить в новое сообщение дату и еще какую-нибудь информацию

dp = Dispatcher()
PARSING_IS_ACTIVE = False

button1 = KeyboardButton(text="Start Parsing")
button2 = KeyboardButton(text="Stop Parsing")
button3 = KeyboardButton(text="Show current")
kb = [[button1, button2], [button3]]
keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@dp.message(CommandStart())
async def message_handler(message: Message) -> Any:
    await message.answer('Привет, начнем?', reply_markup=keyboard)


@dp.message()
async def parser_manager(message: Message == 'Start Parsing', bot) -> Any:
    global PARSING_IS_ACTIVE
    if message.text == 'Start Parsing':
        PARSING_IS_ACTIVE = True
        await message.answer('Парсер запущен', reply_markup=keyboard)
        await start_parser(bot)

    elif message.text == 'Stop Parsing':
        await message.answer('Парсер остановлен', reply_markup=keyboard)
        PARSING_IS_ACTIVE = False

    elif message.text == 'Show current':
        db_connect = DBManager()
        last_request_vacancies = format_vacancies(db_connect.read_data('hh', 'last_request'))
        await message.answer(last_request_vacancies,
                             reply_markup=keyboard,
                             disable_web_page_preview=True)

    else:
        await message.answer('Неизвестная просьба', reply_markup=keyboard)


def format_vacancies(vacancies: dict) -> str:
    formatted_vacancies = []
    for counter, (vacancy_url, vacancy_name) in enumerate(vacancies.items(), start=1):
        formatted_vacancies.append(f'{counter}. <a href="{vacancy_url}">{vacancy_name}</a>')
    formatted_vacancies = '\n'.join(formatted_vacancies)
    return formatted_vacancies


async def start_parser(bot) -> None:
    """
    Активация парсера hh
    Опрос происходит раз период времени от 300 секунд до 500 (рандом)
    """

    while PARSING_IS_ACTIVE:
        hh_parser = Parser()
        data = hh_parser.generate()
        errors = data['errors']
        new_vacancies = data['data']

        if errors or new_vacancies:
            if new_vacancies:
                msg = format_vacancies(new_vacancies)
            else:
                msg = errors

            await bot.send_message(ADMIN_ID,
                                   msg,
                                   disable_web_page_preview=True)

        await asyncio.sleep(random.randint(300, 500))


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.set_my_commands([])
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
