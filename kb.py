from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, BotCommand

# Управение парсингом
start_btn = KeyboardButton(text="Start Parsing")
stop_btn = KeyboardButton(text="Stop Parsing")
check_btn = KeyboardButton(text="Check Parser")

# Управение бд
show_vacancies_btn = KeyboardButton(text="Show Current")

# Инициализация клавиатуры
kb = [[start_btn, stop_btn, check_btn], [show_vacancies_btn]]
kb = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Команды
cmnds = BotCommand(command='start', description='Начать работу с ботом')
