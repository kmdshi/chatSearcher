from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from services import db
from config import Config


moderation_router = Router()


class RejectReason(StatesGroup):
    waiting_for_reason = State()


@moderation_router.callback_query(F.data.startswith("topic_"))
async def handle_moderation_action(callback: CallbackQuery, state: FSMContext):
    action, content_id_str, sender_id_str = callback.data.split(":")
    content_id = int(content_id_str)
    sender_id = int(sender_id_str)
    table = "topics" if action.startswith("topic") else "chats"

    if "approve" in action:
        await db.Database().approve_topic_adding(topicID=content_id)
        await callback.message.edit_text("✅ Топик одобрен.")
        await callback.bot.send_message(
            sender_id,
            "<b>Ваш топик был одобрен</b> ✅",
            parse_mode="HTML"
        )
    else:

        await callback.message.answer("Введите причину отказа:")

        await state.set_state(RejectReason.waiting_for_reason)
        await state.update_data(content_id=content_id, sender_id=sender_id, table=table)


@moderation_router.message(F.text.startswith('/удаление'))
async def handle_delete_command(message: Message):
    admin_ids = [int(id.strip()) for id in Config.ADMIN_IDS.split(",")]

    if message.from_user.id not in admin_ids:
        await message.reply("У вас нет прав для выполнения этой команды.")
        return

    chat_title = message.text.split(' ')[1]

    chat = await db.Database().get_chat_by_title(chat_title)

    if not chat:
        await message.reply("Чат не найден.")
        return

    await db.Database().delete_chat_by_title(chat_title)

    await message.reply(f"Чат с названием {chat_title} был удалён.")


@moderation_router.callback_query(F.data.startswith("chat_"))
async def handle_chat_moderation_action(callback: CallbackQuery, state: FSMContext):
    action, content_id_str, sender_id_str = callback.data.split(":")
    content_id = int(content_id_str)
    sender_id = int(sender_id_str)
    table = "topics" if action.startswith("topic") else "chats"

    if "approve" in action:
        await db.Database().approve_chat_adding(chatID=content_id)
        await callback.message.edit_text("✅ Чат одобрен.")
        await callback.bot.send_message(
            sender_id,
            "<b>Ваш чат был одобрен</b> ✅",
            parse_mode="HTML"
        )
    else:

        await callback.message.answer("Введите причину отказа:")

        await state.set_state(RejectReason.waiting_for_reason)
        await state.update_data(content_id=content_id, sender_id=sender_id, table=table)


@moderation_router.message(StateFilter(RejectReason.waiting_for_reason))
async def process_reject_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    reason = message.text
    sender_id = data["sender_id"]
    content_id = data["content_id"]
    table = data["table"]

    if table == "topics":
        await db.Database().reject_topic_adding(topicID=content_id)
    elif table == "chats":
        await db.Database().reject_chat_adding(chatID=content_id)

    await message.answer("❌ Заявка отклонена и удалена.")
    await message.bot.send_message(
        sender_id,
        f"🚫 <b>Ваша заявка была отклонена</b>.\n\n📝 <i>Причина:</i> {reason}",
        parse_mode="HTML"
    )
    await state.clear()
