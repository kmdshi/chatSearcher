from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters.state import State, StatesGroup
from aiogram_dialog import (
    Dialog, DialogManager, StartMode, Window,
)
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery


class DialogSG(StatesGroup):
    topics = State()
    chats = State()


test_router = Router()


async def get_topics(dialog_manager: DialogManager, **kwargs):
    return {
        "topics": [
            (1, "Философия"),
            (2, "Наука"),
            (3, "Психология"),
            (4, "Искусство"),
            (5, "История"),
            (6, "Технологии"),
            (7, "Музыка"),
            (8, "Кино"),
            (9, "Литература"),
            (10, "Политика"),
        ]
    }


async def get_chats(dialog_manager: DialogManager, **kwargs):
    topic_chats_map = {
        1: [
            (101, "Кантоведы"),
            (102, "Стоики"),
            (103, "Материалисты"),
            (104, "Философия Востока"),
        ],
        2: [
            (201, "Астрофизики"),
            (202, "Биологи"),
            (203, "Химики"),
        ],
        3: [
            (301, "Юнгианцы"),
            (302, "Когнитивная терапия"),
            (303, "Психоанализ"),
        ],
        4: [
            (401, "Современное искусство"),
            (402, "Ренессанс"),
        ],
        5: [
            (501, "Древний мир"),
            (502, "Средневековье"),
            (503, "XX век"),
        ],
        6: [
            (601, "ИИ и Машинное обучение"),
            (602, "Квантовые компьютеры"),
            (603, "Блокчейн"),
        ],
        7: [
            (701, "Классика"),
            (702, "Хип-хоп"),
            (703, "Рок"),
        ],
        8: [
            (801, "Авторское кино"),
            (802, "Голливуд"),
            (803, "Аниме"),
        ],
        9: [
            (901, "Русская классика"),
            (902, "Фэнтези"),
            (903, "Научная фантастика"),
        ],
        10: [
            (1001, "Международные отношения"),
            (1002, "Политическая теория"),
        ],
    }

    selected_topic_id = dialog_manager.dialog_data.get("selected_topic")
    chats = topic_chats_map.get(int(selected_topic_id), [])
    print(f'{chats} CHHHHHHHHATS')
    return {"chats": chats}


async def on_topic_selected(event, source, manager: DialogManager, item_id: int):
    manager.dialog_data["selected_topic"] = item_id
    print(f"Selected topic saved: {item_id}")

    await manager.switch_to(DialogSG.chats)

test_dialog = Dialog(
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
                on_click=lambda *args, **kwargs: None,
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


@test_router.message(CommandStart())
async def start_message_handler(message: Message,  dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.topics, mode=StartMode.RESET_STACK)
