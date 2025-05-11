from aiogram import Router, F
from aiogram.types import Message
from services import db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from keyboards import cancel_keyboard, main_keyboard, mods_keyboard
adding_router = Router()


class TopicForm(StatesGroup):
    name = State()


class ChatForm(StatesGroup):
    topicId = State()
    name = State()
    chat_link = State()


@adding_router.message(F.text == '➕ Добавить тему')
async def start_message_handler(message: Message, state: FSMContext):
    kb = cancel_keyboard.create_cancel_kb()

    await state.set_state(TopicForm.name)
    await message.answer("Какое название у темы?", reply_markup=kb)


@adding_router.message(F.text == '❌ Отмена')
async def cancel_handler(message: Message, state: FSMContext):
    kb = main_keyboard.create_main_kb()

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.reply('Cancelled.', reply_markup=kb)


@adding_router.message(StateFilter(TopicForm.name))
async def process_name(message: Message, state: FSMContext):
    await state.clear()

    main_kb = main_keyboard.create_main_kb()

    sender_id = message.from_user.id
    topic_id = await db.Database().register_topic(message.text, message.from_user.id)
    await message.reply(f"Топик успешно отправлен на модерацию.", reply_markup=main_kb)

    kb = mods_keyboard.approve_buttons(topic_id, sender_id)

    await message.bot.send_message(
        chat_id=1125496753,
        text=f"🆕 Новая заявка на топик:\n\n📌 <b>{message.text}</b>\n👤 От пользователя: @{message.from_user.username or message.from_user.id}",
        reply_markup=kb,
        parse_mode="HTML"
    )


@adding_router.message(F.text == '➕ Добавить чат')
async def start_message_handler(message: Message, state: FSMContext):
    await state.clear()
    kb = cancel_keyboard.create_cancel_kb()

    topics = await db.Database().get_topics()

    if not topics:
        await message.answer("Нет доступных топиков.")
        return

    lines = [f"{topic['text']} — /{topic['id']}" for topic in topics]
    text = "\n".join(lines)

    await message.answer('Выберите в какой топик нужно добавить чат:', reply_markup=kb)
    await message.answer(text)

    await state.set_state(ChatForm.topicId)


@adding_router.message(StateFilter(ChatForm.topicId))
async def process_topic_selection(message: Message, state: FSMContext):
    text = message.text.strip()

    if not text.startswith("/"):
        await message.reply("Пожалуйста, выбери ID в формате /1234.")
        return

    try:
        topic_id = int(text[1:])
    except ValueError:
        await message.reply("Неверный формат ID.")
        return

    await state.update_data(topic_id=topic_id)
    await state.set_state(ChatForm.name)

    await message.answer("Введите название чата:")


@adding_router.message(StateFilter(ChatForm.name))
async def process_chat_name(message: Message, state: FSMContext):
    if len(message.text) > 10:
        message.answer("Название чата должно быть менее 10 символов")
        return

    await state.update_data(name=message.text)
    await state.set_state(ChatForm.chat_link)
    await message.answer("Введите ссылку на чат:")


@adding_router.message(StateFilter(ChatForm.chat_link))
async def process_chat_link(message: Message, state: FSMContext):
    kb = main_keyboard.create_main_kb()

    data = await state.get_data()
    topic_id = data.get("topic_id")
    name = data.get("name")
    link = message.text
    sender_id = message.from_user.id

    if not link.startswith("https://t.me/"):
        await message.reply("Сейчас разрешены только телеграм-чаты. Пожалуйста измените ссылку.")
        return

    chat_id = await db.Database().register_chat(topic_id=topic_id, creator_id=message.from_user.id, chat_name=name, chat_link=link)

    await message.reply(f"Чат успешно отправлен на модерацию.", reply_markup=kb)
    await state.clear()

    kb = mods_keyboard.approve_buttons(
        chat_id, sender_id, True)

    await message.bot.send_message(
        chat_id=1125496753,
        text=f"🆕 Новая заявка на чат:\n\n📌 <b>{message.text}</b>\n👤 От пользователя: @{message.from_user.username or message.from_user.id}",
        reply_markup=kb,
        parse_mode="HTML"
    )
