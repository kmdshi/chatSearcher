from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_main_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Поиск чатов")],
            [KeyboardButton(text="➕ Добавить тему"),
             KeyboardButton(text="➕ Добавить чат")],
            [KeyboardButton(text="📚 Правила"),
             KeyboardButton(text="🛠 Поддержка")]
        ],
        resize_keyboard=True
    )
    return keyboard
