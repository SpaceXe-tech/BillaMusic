import asyncio
import importlib
import logging

from pyrogram import idle

from BillaMusic import app, userbot
from BillaMusic.backup import send
from BillaMusic.core.call import BillaMusic
from BillaMusic.plugins import ALL_MODULES

loop = asyncio.get_event_loop_policy().get_event_loop()


async def init():
    await app.start()
    # for all_module in ALL_MODULES:
    #     importlib.import_module("BillaMusic.plugins" + all_module)
    importlib.import_module("BillaMusic.plugins.admins.callback")
    logging.info("Successfully imported Callback module.")
    await send()
    await userbot.start()
    await BillaMusic.start()
    await BillaMusic.decorators()
    await idle()
    await app.stop()
    await userbot.stop()
    logging.info("Successfully stopped BillaMusic.")


if __name__ == "__main__":
    loop.run_until_complete(init())
