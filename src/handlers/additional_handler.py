from aiogram import Router, F
from aiogram.types import Message
from utils import consts

additional_router = Router()


@additional_router.message(F.text == '📚 Правила')
async def rules_message(message: Message):
    await message.answer(f'{consts.Constants.rules}', parse_mode="HTML")


@additional_router.message(F.text == '🛠 Поддержка')
async def help_message(message: Message):
    await message.answer(f'По вопросом бота и/или нарушениям к @helpernow')
