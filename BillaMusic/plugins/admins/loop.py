from pyrogram import filters
from pyrogram.types import Message

from BillaMusic import app
from BillaMusic.utils.database import get_loop, set_loop
from BillaMusic.utils.decorators import AdminRightsCheck
from BillaMusic.utils.inline import close_markup


@app.on_message(filters.command(["loop", "cloop"]) & filters.group)
@AdminRightsCheck
async def admins(cli, message: Message, chat_id):
    usage = "Example: /loop [enable/disable]\n/loop 8"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip()
    if state.isnumeric():
        state = int(state)
        if 1 <= state <= 10:
            got = await get_loop(chat_id)
            if got != 0:
                state = got + state
            if int(state) > 10:
                state = 10
            await set_loop(chat_id, state)
            return await message.reply_text(
                text="Loop enabled for {} times by {}".format(
                    state, message.from_user.mention
                ),
                reply_markup=close_markup(),
            )
        else:
            return await message.reply_text("Only loop digits between 1 to 10 are allowed ie Min 1 & Max 10 loop Per Song.")
    elif state.lower() == "enable":
        await set_loop(chat_id, 10)
        return await message.reply_text(
            text="Loop Has Been Turned On For {} Times By {}".format(
                state, message.from_user.mention
            ),
            reply_markup=close_markup(),
        )
    elif state.lower() == "disable":
        await set_loop(chat_id, 0)
        return await message.reply_text(
            "Loop Has Been Turned Off By {}".format(message.from_user.mention),
            reply_markup=close_markup(),
        )
    else:
        return await message.reply_text(usage)
