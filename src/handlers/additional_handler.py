from aiogram import Router, F
from aiogram.types import Message


additional_router = Router()


@additional_router.message(F.text == '📚 Правила')
async def rules_message(message: Message):
    await message.answer(f'Правила есть - не делать хуйню')


@additional_router.message(F.text == '🛠 Поддержка')
async def help_message(message: Message):
    await message.answer(f'По вопросом бота @kmdshi')
