from pyrogram.types import InlineKeyboardButton

import config
from BillaMusic import app


def start_panel():
    buttons = [
        [
            InlineKeyboardButton(
                text="Add Me", url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text="Support Group", url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel():
    buttons = [
        [
            InlineKeyboardButton(
                text="Try Me Now", url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text="Commands", callback_data="settings_back_helper"),
        ],
        [
            InlineKeyboardButton(text="Support Group", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text="Billa Updates", url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons
