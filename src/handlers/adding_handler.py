from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from services import db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram_dialog import (
    Dialog, DialogManager, StartMode, Window,
)
from aiogram_dialog.widgets.common import ManagedWidget
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back
from aiogram_dialog.widgets.text import Const, Format
from keyboards import cancel_keyboard, main_keyboard, mods_keyboard
adding_router = Router()


class TopicAddingSG(StatesGroup):
    topics = State()


class TopicForm(StatesGroup):
    name = State()


class ChatForm(StatesGroup):
    topicId = State()
    name = State()
    chat_link = State()


async def get_topics(dialog_manager: DialogManager, **kwargs):
    raw_topics = await db.Database().get_topics()

    return {
        "topics": [] if raw_topics is None else [
            (row['id'], row['text'])
            for row in raw_topics
        ]
    }


async def on_topic_selected(callback: CallbackQuery, widget: ManagedWidget, manager: DialogManager, item_id: str):
    if callback.message:
        await callback.message.delete()

    if manager.has_context():
        await manager.done()

    state: FSMContext = manager.middleware_data.get("state")

    await state.update_data(topicId=item_id)

    await callback.message.answer(
        f"🌟 <b>Выбран топик</b>: <code>{item_id}</code>\n\nТеперь выберите название для чата!", parse_mode="HTML"
    )

    await callback.message.answer(
        "🔹 <b>2. Введите название чата ниже:</b>", parse_mode="HTML"
    )

    await state.set_state(ChatForm.name)

chats_adding_dialog = Dialog(
    Window(
        Const("Выберите топик ниже 👇"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="topics_select",
                item_id_getter=lambda item: item[0],
                items="topics",
                on_click=on_topic_selected,
            ),
            id="scroll_topics",
            width=1,
            height=6,
        ),
        state=TopicAddingSG.topics,
        getter=get_topics,
    ),
)


@adding_router.message(F.text == '➕ Добавить тему')
async def start_message_handler(message: Message, state: FSMContext):
    kb = cancel_keyboard.create_cancel_kb()

    await state.set_state(TopicForm.name)
    await message.answer(
        "<b>📌 Какое название у темы?</b>\n\n<i>Пожалуйста, введите название топика ниже:</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )


@adding_router.message(F.text == '❌ Отмена')
async def cancel_handler(message: Message, state: FSMContext):
    kb = main_keyboard.create_main_kb()

    current_state = await state.get_state()
    if current_state is None:
        await message.reply("<i>🚫 Нет активного процесса для отмены.</i>", parse_mode="HTML")
        return

    await state.clear()
    await message.reply(
        "<b>✅ Операция отменена.</b>\n\n<i>Вы вернулись в главное меню.</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )


@adding_router.message(StateFilter(TopicForm.name))
async def process_topic_name(message: Message, state: FSMContext):
    await state.clear()

    main_kb = main_keyboard.create_main_kb()

    sender_id = message.from_user.id

    topic_name = message.text

    if len(topic_name) > 25:
        await message.answer(
            "<b>❌ Название топика должно быть менее 25 символов</b>\n\n<i>Пожалуйста, выберите более короткое название.</i>",
            parse_mode="HTML"
        )
        return

    topic_id = await db.Database().register_topic(topic_name, message.from_user.id)

    await message.reply(
        "<b>✅ Топик успешно отправлен на модерацию.</b>",
        reply_markup=main_kb,
        parse_mode="HTML"
    )

    kb = mods_keyboard.approve_buttons(topic_id, sender_id)

    await message.bot.send_message(
        chat_id=1125496753,
        text=f"🆕 Новая заявка на топик:\n\n📌 <b>{message.text}</b>\n👤 От пользователя: @{message.from_user.username or message.from_user.id}",
        reply_markup=kb,
        parse_mode="HTML"
    )


@adding_router.message(F.text == '➕ Добавить чат')
async def start_message_handler(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()
    kb = cancel_keyboard.create_cancel_kb()

    topics = await db.Database().get_topics()

    if not topics:
        await message.answer(
            "<b>❌ Нет доступных топиков.</b>\n\n<i>Пожалуйста, попробуйте позже или создайте новый топик!</i>",
            parse_mode="HTML"
        )
        return

    await message.answer("🔹<b>1. Выберите топик</b>", reply_markup=kb, parse_mode="HTML")
    await state.set_state(ChatForm.topicId)

    await dialog_manager.start(TopicAddingSG.topics, mode=StartMode.NEW_STACK)


@adding_router.message(StateFilter(ChatForm.name))
async def process_chat_name(message: Message, state: FSMContext):
    if len(message.text) > 10:
        await message.answer(
            "<b>Название чата должно быть менее 10 символов.</b> ❌\n\n<i>Пожалуйста, попробуйте снова!</i>",
            parse_mode="HTML"
        )
        return

    await state.update_data(name=message.text)
    await state.set_state(ChatForm.chat_link)
    await message.answer(
        "<b>Введите ссылку на чат:</b> 🔗",
        parse_mode="HTML"
    )


@adding_router.message(StateFilter(ChatForm.chat_link))
async def process_chat_link(message: Message, state: FSMContext):
    kb = main_keyboard.create_main_kb()

    data = await state.get_data()
    topic_id = data.get("topic_id")
    name = data.get("name")
    link = message.text
    sender_id = message.from_user.id

    if not link.startswith("https://t.me/"):
        await message.reply(
            "<b>Сейчас разрешены только телеграм-чаты.</b> ❌ Пожалуйста, измените ссылку.",
            parse_mode="HTML"
        )
        return

    chat_id = await db.Database().register_chat(topic_id=topic_id, creator_id=message.from_user.id, chat_name=name, chat_link=link)

    await message.reply(
        "<b>Чат успешно отправлен на модерацию.</b> ✅\n\n<i>Ожидайте проверки.</i> ⏳",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.clear()

    kb = mods_keyboard.approve_buttons(
        chat_id, sender_id, True)

    await message.bot.send_message(
        chat_id=1125496753,
        text=f"🆕 Новая заявка на чат:\n\n📌 <b>{message.text}</b>\n👤 От пользователя: @{message.from_user.username or message.from_user.id}",
        reply_markup=kb,
        parse_mode="HTML"
    )
