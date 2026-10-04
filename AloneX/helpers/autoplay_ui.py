from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AloneX import db
from AloneX.helpers import buttons


def _append_autoplay(markup: InlineKeyboardMarkup, label: str, callback_data: str):
    rows = [list(row) for row in markup.inline_keyboard]
    rows.append([InlineKeyboardButton(label, callback_data=callback_data)])
    return InlineKeyboardMarkup(rows)


def _insert_seek_buttons_above_autoplay(markup: InlineKeyboardMarkup):
    rows = [list(row) for row in markup.inline_keyboard]
    seek_row = [
        InlineKeyboardButton(
            "-𝟣𝟧ˢ", callback_data="seekback_15", style=ButtonStyle.PRIMARY
        ),
        InlineKeyboardButton(
            "𝟣𝟧ˢ+", callback_data="seek_15", style=ButtonStyle.PRIMARY
        ),
    ]

    # Auto Play is the row immediately before Updates/Close.
    # Put the 15-second seek controls directly above Auto Play.
    if len(rows) >= 2:
        rows.insert(len(rows) - 2, seek_row)
    else:
        rows.append(seek_row)

    return InlineKeyboardMarkup(rows)


def _replace_add_me_with_autoplay(
    markup: InlineKeyboardMarkup, label: str, callback_data: str
):
    rows = [list(row) for row in markup.inline_keyboard]
    autoplay_row = [
        InlineKeyboardButton(
            label, callback_data=callback_data, style=ButtonStyle.PRIMARY
        )
    ]

    # buttons.controls() puts the Add Me row immediately before Updates/Close.
    # Replace that row so Autoplay occupies the exact same position.
    if len(rows) >= 2:
        rows[-2] = autoplay_row
    else:
        rows.append(autoplay_row)

    return InlineKeyboardMarkup(rows)


async def autoplay_label(chat_id: int) -> str:
    return (
        "ᴧᴜᴛσᴘʟᴧʏ: єηᴧʙʟєᴅ"
        if await db.get_autoplay(chat_id)
        else "ᴧᴜᴛσᴘʟᴧʏ: ᴅɪsᴧʙʟєᴅ"
    )


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
    markup = _replace_add_me_with_autoplay(
        markup, await autoplay_label(chat_id), "autoplay:toggle"
    )
    return _insert_seek_buttons_above_autoplay(markup)


async def help_with_autoplay(chat_id: int, lang, back: bool = False):
    markup = buttons.help_markup(lang, back)
    if back:
        return markup
    rows = [list(row) for row in markup.inline_keyboard]
    rows.append(
        [
            InlineKeyboardButton(
                "ᴧᴜᴛσᴘʟᴧʏ",
                callback_data="help autoplay",
                style=ButtonStyle.PRIMARY,
            )
        ]
    )
    return InlineKeyboardMarkup(rows)


async def queue_with_autoplay(chat_id: int, status: str, playing: bool):
    markup = buttons.queue_markup(chat_id, status, playing)
    rows = [list(row) for row in markup.inline_keyboard]
    rows.append(
        [
            InlineKeyboardButton(
                await autoplay_label(chat_id),
                callback_data="autoplay:toggle",
                style=ButtonStyle.PRIMARY,
            )
        ]
    )
    return InlineKeyboardMarkup(rows)
