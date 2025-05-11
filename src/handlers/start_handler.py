from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.main_keyboard import create_main_kb
from services import db


start_router = Router()


@start_router.message(CommandStart())
async def start_message_handler(message: Message):
    kb = create_main_kb()
    await db.Database().register_user(message.from_user.id)
    await message.answer(f'Хе-хе! Совсем скоро ^-^', reply_markup=kb)
