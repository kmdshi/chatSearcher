from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def approve_buttons(content_id, sender_id, is_chat=False):
    prefix = "chat" if is_chat else "topic"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"{prefix}_approve:{content_id}:{sender_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"{prefix}_reject:{content_id}:{sender_id}")
        ]
    ])