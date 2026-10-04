from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AloneX import db
from AloneX.helpers import buttons


def _append_autoplay(markup: InlineKeyboardMarkup, label: str, callback_data: str):
    rows = [list(row) for row in markup.inline_keyboard]
    rows.append([InlineKeyboardButton(label, callback_data=callback_data)])
    return InlineKeyboardMarkup(rows)


async def autoplay_label(chat_id: int) -> str:
    return "♫ AUTOPLAY: ON" if await db.get_autoplay(chat_id) else "♫ AUTOPLAY: OFF"


async def controls_with_autoplay(
    chat_id: int,
    status: str = None,
    timer: str = None,
    remove: bool = False,
):
    markup = buttons.controls(
        chat_id=chat_id,
        status=status,
        timer=timer,
        remove=remove,
    )
    return _append_autoplay(markup, await autoplay_label(chat_id), "autoplay:toggle")


async def help_with_autoplay(chat_id: int, lang, back: bool = False):
    markup = buttons.help_markup(lang, back)
    return _append_autoplay(
        markup, await autoplay_label(chat_id), "autoplay:toggle:help"
    )
