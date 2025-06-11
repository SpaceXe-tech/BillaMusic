# BillaMusic/core/call.py
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, filters
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    PyTgCallsException,  # Fallback for AlreadyJoinedError
)
from ntgcalls import TelegramServerError
from pytgcalls.types import AudioQuality, Update, VideoQuality, MediaStream, ChatUpdate
from pytgcalls.types.stream import StreamAudioEnded

import config
from BillaMusic import YouTube, app
from BillaMusic.misc import db
from BillaMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from BillaMusic.utils.exceptions import (
    AssistantErr,
    VoiceChatError,
    StreamError,
    DownloadError,
    ConfigError,
    DatabaseError,
)
from BillaMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from BillaMusic.utils.inline.play import stream_markup
from BillaMusic.utils.stream.autoclear import auto_clean

autoend = {}
counter = {}
loop = asyncio.get_event_loop_policy().get_event_loop()


async def _clear_(chat_id):
    try:
        db[chat_id] = []
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
    except Exception as e:
        raise DatabaseError(f"Failed to clear chat data: {str(e)}", chat_id=chat_id)


class Call(PyTgCalls):
    def __init__(self):
        try:
            self.userbot1 = Client(
                name="Billa1",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING1),
            )
            self.one = PyTgCalls(
                self.userbot1,
                cache_duration=100,
            )
            self.userbot2 = Client(
                name="Billa2",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING2),
            )
            self.two = PyTgCalls(
                self.userbot2,
                cache_duration=100,
            )
            self.userbot3 = Client(
                name="Billa3",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING3),
            )
            self.three = PyTgCalls(
                self.userbot3,
                cache_duration=100,
            )
            self.userbot4 = Client(
                name="Billa4",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING4),
            )
            self.four = PyTgCalls(
                self.userbot4,
                cache_duration=100,
            )
            self.userbot5 = Client(
                name="Billa5",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING5),
            )
            self.five = PyTgCalls(
                self.userbot5,
                cache_duration=100,
            )
        except Exception as e:
            raise ConfigError(f"Failed to initialize userbots: {str(e)}")
   
  async def pause_stream(self, chat_id: int):
      assistant = await group_assistant(self, chat_id)
      try:
          await assistant.pause_stream(chat_id)
      except Exception as e:
          raise VoiceChatError(f"Failed to pause stream: {str(e)}", chat_id=chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await assistant.resume_stream(chat_id)
        except Exception as e:
            raise VoiceChatError(f"Failed to resume stream: {str(e)}", chat_id=chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except Exception as e:
            raise VoiceChatError(f"Failed to stop stream: {str(e)}", chat_id=chat_id)

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_call(chat_id)
        except Exception as e:
            logging.error(f"Failed to force stop stream for userbot1: {e}")
        try:
            if config.STRING2:
                await self.two.leave_call(chat_id)
        except Exception as e:
            logging.error(f"Failed to force stop stream for userbot2: {e}")
        try:
            if config.STRING3:
                await self.three.leave_call(chat_id)
        except Exception as e:
            logging.error(f"Failed to force stop stream for userbot3: {e}")
        try:
            if config.STRING4:
                await self.four.leave_call(chat_id)
        except Exception as e:
            logging.error(f"Failed to force stop stream for userbot4: {e}")
        try:
            if config.STRING5:
                await self.five.leave_call(chat_id)
        except Exception as e:
            logging.error(f"Failed to force stop stream for userbot5: {e}")
        try:
            await _clear_(chat_id)
        except Exception as e:
            raise DatabaseError(f"Failed to clear chat data during force stop: {str(e)}", chat_id=chat_id)

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        try:
            if str(speed) != "1.0":
                base = os.path.basename(file_path)
                chatdir = os.path.join(os.getcwd(), "playback", str(speed))
                if not os.path.isdir(chatdir):
                    os.makedirs(chatdir)
                out = os.path.join(chatdir, base)
                if not os.path.isfile(out):
                    if str(speed) == "0.5":
                        vs = 2.0
                    if str(speed) == "0.75":
                        vs = 1.35
                    if str(speed) == "1.5":
                        vs = 0.68
                    if str(speed) == "2.0":
                        vs = 0.5
                    proc = await asyncio.create_subprocess_shell(
                        cmd=(
                            "ffmpeg "
                            "-i "
                            f"{file_path} "
                            "-filter:v "
                            f"setpts={vs}*PTS "
                            "-filter:a "
                            f"atempo={speed} "
                            f"{out}"
                        ),
                        stdin=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    await proc.communicate()
            else:
                out = file_path
            dur = await loop.run_in_executor(None, check_duration, out)
            dur = int(dur)
            played, con_seconds = speed_converter(playing[0]["played"], speed)
            duration = seconds_to_min(dur)
            stream = (
                MediaStream(
                    out,
                    audio_parameters=AudioQuality.STUDIO,
                    video_parameters=VideoQuality.UHD_4K,
                    ffmpeg_parameters=f"-ss {played} -to {duration}",
                )
                if playing[0]["streamtype"] == "video"
                else MediaStream(
                    out,
                    audio_parameters=AudioQuality.STUDIO,
                    ffmpeg_parameters=f"-ss {played} -to {duration}",
                )
            )
            if str(db[chat_id][0]["file"]) == str(file_path):
                await assistant.play(chat_id, stream)
            else:
                raise StreamError("File mismatch during stream playback", stream_type=playing[0]["streamtype"])
            if str(db[chat_id][0]["file"]) == str(file_path):
                exis = (playing[0]).get("old_dur")
                if not exis:
                    db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                    db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
                db[chat_id][0]["played"] = con_seconds
                db[chat_id][0]["dur"] = duration
                db[chat_id][0]["seconds"] = dur
                db[chat_id][0]["speed_path"] = out
                db[chat_id][0]["speed"] = speed
        except Exception as e:
            raise StreamError(f"Failed to process stream speedup: {str(e)}", stream_type=playing[0]["streamtype"])

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except Exception as e:
            raise DatabaseError(f"Failed to clear queue: {str(e)}", chat_id=chat_id)
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except Exception as e:
            raise VoiceChatError(f"Failed to leave call: {str(e)}", chat_id=chat_id)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
    ):  
        assistant = await group_assistant(self, chat_id)
        try:
            if video:
                stream = MediaStream(
                    link,
                    audio_parameters=AudioQuality.STUDIO,
                    video_parameters=VideoQuality.UHD_4K,
                )
            else:
                stream = MediaStream(
                    link,
                    audio_parameters=AudioQuality.STUDIO,
                )
            await assistant.play(chat_id, stream)
        except NoActiveGroupCall:
            raise VoiceChatError("Please start voice chat first.", chat_id=chat_id)
        except PyTgCallsException as e:  # Fallback for AlreadyJoinedError
            raise VoiceChatError(f"Assistant already in VC or other error: {str(e)}", chat_id=chat_id)
        except TelegramServerError:
            raise VoiceChatError(
                "Telegram is having internal problems. Try restarting voice chat or wait for sometime.",
                chat_id=chat_id
            )
        except Exception as e:
            logging.error(e)
            raise VoiceChatError(f"Unexpected error joining call: {str(e)}", chat_id=chat_id)
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)
