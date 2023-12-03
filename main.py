from random import randint
import asyncio

from aiogram import F, Router, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from mongo_db import DBManager
import settings
from kb import kb, cmnds
from parsers.manager import Manager

bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)
pars_is_on = False
router = Router()


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.set_my_commands([cmnds])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def format_vacancies(vacancies: dict) -> str:
    formatted_vacancies = []
    for counter, (vacancy_url, vacancy_name) in enumerate(vacancies.items(), start=1):
        formatted_vacancies.append(f'{counter}. <a href="{vacancy_url}">{vacancy_name}</a>')
    formatted_vacancies = '\n'.join(formatted_vacancies)
    return formatted_vacancies


async def start_parser(msg: Message) -> None:
    """
    Активация парсинга
    Опрос происходит раз период времени от 300 секунд до 500 (рандом)
    """

    await msg.answer(f'Парсер запущен pars_is_on={pars_is_on}')

    while pars_is_on:
        data = Manager().generate()
        errors = data['errors']
        new_vacancies = data['data']

        if errors or new_vacancies:
            if new_vacancies:
                msg = await format_vacancies(new_vacancies)
            else:
                msg = errors

            await bot.send_message(settings.ADMIN_ID,
                                   msg,
                                   disable_web_page_preview=True)

        await asyncio.sleep(randint(300, 500))


@router.message(CommandStart())
async def message_handler(message: Message) -> None:
    await message.answer('Привет, начнем?', reply_markup=kb)


@router.message(F.text == "Start Parsing")
async def parser_manager(message: Message) -> None:
    global pars_is_on
    pars_is_on = True
    await start_parser(message)


@router.message(F.text == "Stop Parsing")
async def parser_manager(message: Message) -> None:
    global pars_is_on
    pars_is_on = False
    await message.answer(f'Парсер остановлен pars_is_on={pars_is_on}')


@router.message(F.text == "Check Parser")
async def parser_manager(message: Message) -> None:
    await message.answer(f'Статус парсера pars_is_on={pars_is_on}')


@router.message(F.text == "Show Current")
async def parser_manager(message: Message) -> None:
    db_connect = DBManager()
    last_request_vacancies = format_vacancies(db_connect.read_data('hh', 'last_request'))
    await message.answer(await last_request_vacancies,
                         reply_markup=kb,
                         disable_web_page_preview=True)


if __name__ == "__main__":
    asyncio.run(main())
