# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.

from pyrogram import enums, filters, types

from AloneX import app, db, lang


@app.on_message(
    filters.command(["autoplay"])
    & (filters.group | filters.private)
    & ~app.bl_users
)
@lang.language()
async def _autoplay(_, m: types.Message):
    if m.chat.type != enums.ChatType.PRIVATE:
        if m.from_user.id not in app.sudoers:
            admins = await db.get_admins(m.chat.id)
            if m.from_user.id not in admins:
                return await m.reply_text(m.lang["user_no_perms"])

    enabled = not await db.get_autoplay(m.chat.id)
    await db.set_autoplay(m.chat.id, enabled)
    await m.reply_text(f"♫ Autoplay {'ON' if enabled else 'OFF'}")
