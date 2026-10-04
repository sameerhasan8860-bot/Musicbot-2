from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AloneX import db
from AloneX.helpers import buttons


async def controls_with_autoplay(chat_id: int, status: str = None):
    """Return the normal player controls with an autoplay toggle row."""
    markup = buttons.controls(chat_id, status=status)
    enabled = await db.get_autoplay(chat_id)
    label = "♫ AUTOPLAY: ON" if enabled else "♫ AUTOPLAY: OFF"
    rows = [list(row) for row in markup.inline_keyboard]
    rows.append([InlineKeyboardButton(label, callback_data="autoplay:toggle")])
    return InlineKeyboardMarkup(rows)
