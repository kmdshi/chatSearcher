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
    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "Выбирай тему, создавай чаты или присоединяйся к существующим\n\n"
        "И, конечно, главное — находи единомышленников и круто проводи время!",
        reply_markup=kb,
        parse_mode="HTML"
    )
