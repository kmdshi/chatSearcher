from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.state import State, StatesGroup
from aiogram_dialog import (
    Dialog, DialogManager, StartMode, Window,
)
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
from services import db
from aiogram_dialog.widgets.common import ManagedWidget


class DialogSG(StatesGroup):
    topics = State()
    chats = State()


chats_router = Router()


async def get_topics(dialog_manager: DialogManager, **kwargs):
    raw_topics = await db.Database().get_topics()

    return {
        "topics": [] if raw_topics is None else [
            (row['id'], row['text'])
            for row in raw_topics
        ]
    }


async def get_chats(dialog_manager: DialogManager, **kwargs):
    topic_id = dialog_manager.dialog_data["selected_topic"]
    raw_chats = await db.Database().get_topic_chats(topic_id)

    return {
        "chats": [] if raw_chats is None else [
            (row['link'], row['title'])
            for row in raw_chats
        ]
    }


async def on_topic_selected(event, source, manager: DialogManager, item_id: int, **kwargs):
    manager.dialog_data["selected_topic"] = item_id
    await manager.switch_to(DialogSG.chats)


async def on_chat_click(callback: CallbackQuery, widget: ManagedWidget, manager: DialogManager, item_id: str):
    await callback.answer()
    await callback.message.answer(f"Ссылка на чат: {item_id}")


chats_dialog = Dialog(
    Window(
        Const("Выбери тему:"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="topic_select",
                item_id_getter=lambda item: item[0],
                items="topics",
                on_click=on_topic_selected,
            ),
            id="scroll_topics",
            width=1,
            height=6,
        ),
        state=DialogSG.topics,
        getter=get_topics,
    ),
    Window(
        Const("Чаты по теме:"),
        ScrollingGroup(
            Select(
                Format("💬 {item[1]}"),
                id="chat_select",
                item_id_getter=lambda item: item[0],
                items="chats",
                on_click=on_chat_click,
            ),
            id="scroll_chats",
            width=1,
            height=5,
        ),
        Back(),
        state=DialogSG.chats,
        getter=get_chats,
    )
)


@chats_router.message(F.text != '🔍 Поиск чатов')
async def default_message_handler(message: Message, dialog_manager: DialogManager):
    if dialog_manager.has_context():
        await dialog_manager.done()


@chats_router.message(F.text == '🔍 Поиск чатов')
async def search_chat_msg(message: Message,  dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.topics, mode=StartMode.NEW_STACK)
