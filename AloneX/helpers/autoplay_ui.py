from pyrogram.types import ButtonStyle, InlineKeyboardButton, InlineKeyboardMarkup

from AloneX import db
from AloneX.helpers import buttons


def _append_autoplay(markup: InlineKeyboardMarkup, label: str, callback_data: str):
    rows = [list(row) for row in markup.inline_keyboard]
    rows.append([InlineKeyboardButton(label, callback_data=callback_data)])
    return InlineKeyboardMarkup(rows)


def _replace_add_me_with_autoplay(
    markup: InlineKeyboardMarkup, label: str, callback_data: str
):
    rows = [list(row) for row in markup.inline_keyboard]
    autoplay_row = [InlineKeyboardButton(label, callback_data=callback_data, style=ButtonStyle.SUCCESS)]

    # buttons.controls() puts the Add Me row immediately before Updates/Close.
    # Replace that row so Autoplay occupies the exact same position.
    if len(rows) >= 2:
        rows[-2] = autoplay_row
    else:
        rows.append(autoplay_row)

    return InlineKeyboardMarkup(rows)


async def autoplay_label(chat_id: int) -> str:
    return ("ᴧᴜᴛσᴘʟᴧʏ: єηᴧʙʟєᴅ" if await db.get_autoplay(chat_id) else "ᴧᴜᴛσᴘʟᴧʏ: ᴅɪsᴧʙʟєᴅ")


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
    return _replace_add_me_with_autoplay(
        markup, await autoplay_label(chat_id), "autoplay:toggle"
    )


async def help_with_autoplay(chat_id: int, lang, back: bool = False):
    markup = buttons.help_markup(lang, back)
    if back:
        return markup
    rows = [list(row) for row in markup.inline_keyboard]\n    rows.append([InlineKeyboardButton("ᴧᴜᴛσᴘʟᴧʏ", callback_data="help autoplay", style=ButtonStyle.SUCCESS)])\n    return InlineKeyboardMarkup(rows)


async def queue_with_autoplay(chat_id: int, status: str, playing: bool):
    markup = buttons.queue_markup(chat_id, status, playing)
    return _append_autoplay(
        markup, await autoplay_label(chat_id), "autoplay:toggle"
    )
