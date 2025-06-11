from pyrogram import filters
from pyrogram.types import Message

from BillaMusic import app
from BillaMusic.core.call import BillaMusic
from BillaMusic.utils.database import is_music_playing, music_off
from BillaMusic.utils.decorators import AdminRightsCheck
from BillaMusic.utils.inline import close_markup


@app.on_message(filters.command(["pause", "cpause"]) & filters.group)
@AdminRightsCheck
async def pause_admin(cli, message: Message, chat_id):
    if not await is_music_playing(chat_id):
        return await message.reply_text("Song is already paused.")
    await music_off(chat_id)
    await BillaMusic.pause_stream(chat_id)
    await message.reply_text(
        "Song has been paused by {}".format(message.from_user.mention),
        reply_markup=close_markup(),
    )
