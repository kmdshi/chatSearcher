from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_cancel_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True
    )
    return keyboard
