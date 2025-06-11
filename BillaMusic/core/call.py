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
    PyTgCallsAlreadyRunning,  # Specific exception for already joined
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

    async def check_active_call(self, chat_id: int) -> bool:
        """Check if a voice chat is active in the given chat."""
        assistant = await group_assistant(self, chat_id)
        try:
            participants = await assistant.get_participants(chat_id)
            return len(participants) > 0
        except NoActiveGroupCall:
            return False
        except Exception as e:
            raise VoiceChatError(f"Failed to check active call: {str(e)}", chat_id=chat_id)

    async def log_error(self, chat_id: int, method: str, error: Exception):
        """Log an error with chat context and method details."""
        error_msg = f"Error in {method} for chat {chat_id}: {str(error)}"
        logging.error(error_msg)
        try:
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=error_msg,
                disable_web_page_preview=True
            )
        except Exception as e:
            logging.error(f"Failed to send error to logger: {str(e)}")

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            if not db.get(chat_id) or db[chat_id][0]["played"] == 0:
                raise VoiceChatError("No stream is currently playing.", chat_id=chat_id)
            await assistant.pause_stream(chat_id)
            await app.send_message(
                chat_id=chat_id,
                text="Stream paused successfully.",
                disable_web_page_preview=True
            )
        except Exception as e:
            raise VoiceChatError(f"Failed to pause stream: {str(e)}", chat_id=chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            if db.get(chat_id) and db[chat_id][0]["played"] != 0:
                raise VoiceChatError("Stream is already playing.", chat_id=chat_id)
            await assistant.resume_stream(chat_id)
            await app.send_message(
                chat_id=chat_id,
                text="Stream resumed successfully.",
                disable_web_page_preview=True
            )
        except Exception as e:
            raise VoiceChatError(f"Failed to resume stream: {str(e)}", chat_id=chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
            await app.send_message(
                chat_id=chat_id,
                text="Stream stopped and voice chat left successfully.",
                disable_web_page_preview=True
            )
        except Exception as e:
            raise VoiceChatError(f"Failed to stop stream: {str(e)}", chat_id=chat_id)

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_call(chat_id)
        except Exception as e:
            await self.log_error(chat_id, "stop_stream_force (userbot1)", e)
        try:
            if config.STRING2:
                await self.two.leave_call(chat_id)
        except Exception as e:
            await self.log_error(chat_id, "stop_stream_force (userbot2)", e)
        try:
            if config.STRING3:
                await self.three.leave_call(chat_id)
        except Exception as e:
            await self.log_error(chat_id, "stop_stream_force (userbot3)", e)
        try:
            if config.STRING4:
                await self.four.leave_call(chat_id)
        except Exception as e:
            await self.log_error(chat_id, "stop_stream_force (userbot4)", e)
        try:
            if config.STRING5:
                await self.five.leave_call(chat_id)
        except Exception as e:
            await self.log_error(chat_id, "stop_stream_force (userbot5)", e)
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
                    db[chat_id][0]["cuts"] = db[chat_id][0]["seconds"]
                db[chat_id][0]["passed"] = con_seconds
                db[chat_id][0]["dur"] = duration
                db[chat_id][0]["seconds"] = dur
                db[chat_id][0]["speed_path"] = out
                db[chat_id][0]["speed"] = speed
        except Exception as e:
            raise StreamError(f"Failed to process stream speedup: {str(e)}", stream_type=playing[0]["streamtype"])

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None):
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
        except Exception as e:
            raise StreamError(f"Failed to skip stream: {str(e)}", stream_type="video" if video else "audio")

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        try:
            stream = (
                MediaStream(
                    file_path,
                    audio_parameters=AudioQuality.STUDIO,
                    video_parameters=VideoQuality.UHD_4K,
                    ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
                )
                if mode == "video"
                else MediaStream(
                    file_path,
                    audio_parameters=AudioQuality.STUDIO,
                    ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
                )
            )
            await assistant.play(chat_id, stream)
        except Exception as e:
            raise StreamError(f"Failed to seek stream: {str(e)}", stream_type=mode)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        try:
            await assistant.play(config.LOGGER_ID, MediaStream(link))
            await asyncio.sleep(0.2)
            await assistant.leave_call(config.LOGGER_ID)
        except Exception as e:
            raise VoiceChatError(f"Failed to stream call: {str(e)}", chat_id=config.LOGGER_ID)

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
        if not await self.check_active_call(chat_id):
            raise VoiceChatError("Please start voice chat first.", chat_id=chat_id)
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
            raise VoiceChatError("Voice chat is no longer active.", chat_id=chat_id)
        except PyTgCallsAlreadyRunning:
            raise VoiceChatError("Assistant is already in a voice chat. Try /reboot.", chat_id=chat_id)
        except TelegramServerError:
            raise VoiceChatError(
                "Telegram is having internal problems. Try restarting voice chat or wait for sometime.",
                chat_id=chat_id
            )
        except Exception as e:
            await self.log_error(chat_id, "join_call", e)
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

    async def play(self, client, chat_id, max_retries: int = 3):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                await client.leave_call(chat_id)
                return
        except Exception as e:
            raise DatabaseError(f"Failed to process queue: {str(e)}", chat_id=chat_id)
        queued = check[0]["file"]
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        try:
            db[chat_id][0]["played"] = 0
            if exis := (check[0]).get("old_dur"):
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = str(streamtype) == "video"
            if "live_" in queued:
                for attempt in range(max_retries):
                    try:
                        n, link = await YouTube.video(videoid, True)
                        if n == 0:
                            raise StreamError("Failed to fetch live stream URL", stream_type=streamtype)
                        stream = (
                            MediaStream(
                                link,
                                audio_parameters=AudioQuality.STUDIO,
                                video_parameters=VideoQuality.UHD_4K,
                            )
                            if video
                            else MediaStream(
                                link,
                                audio_parameters=AudioQuality.STUDIO,
                            )
                        )
                        await client.play(chat_id, stream)
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        raise StreamError(f"Failed to play live stream after {max_retries} attempts: {str(e)}", stream_type=streamtype)
                button = stream_markup(chat_id)
                ke = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=ke.format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:30],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    disable_web_page_preview=True
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, "Next Track Is Downloading... Please wait.")
                for attempt in range(max_retries):
                    try:
                        file_path, direct = await YouTube.download(videoid, mystic, videoid=True, video=video)
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        await mystic.delete()
                        raise DownloadError(f"Failed to download video after {max_retries} attempts: {str(e)}", url=videoid)
                stream = (
                    MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.UHD_4K,
                    )
                    if video
                    else MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.STUDIO,
                    )
                )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    raise StreamError(f"Failed to play downloaded stream: {str(e)}", stream_type=streamtype)
                button = stream_markup(chat_id)
                await mystic.delete()
                ke = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=ke.format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:30],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    disable_web_page_preview=True
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                stream = (
                    MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.UHD_4K
                    )
                    if str(streamtype) == "video"
                    else MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.STUDIO
                    )
                )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    raise StreamError(f"Failed to play index stream: {str(e)}", stream_type=streamtype)
                button = stream_markup(chat_id)
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text="<b>Started Streaming</b>\n\n<b>Stream Type:</b> Live Stream [URL]\n<b>Requested by:</b> {}".format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                    disable_web_page_preview=True
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                stream = (
                    MediaStream(
                        queued,
                        audio_parameters=AudioQuality.STUDIO,
                        video_parameters=VideoQuality.UHD_4K
                    )
                    if video
                    else MediaStream(
                        queued,
                        audio_parameters=AudioQuality.STUDIO
                    )
                )
                try:
                    await client.play(chat_id, stream)
                except Exception as e:
                    raise StreamError(f"Failed to play stream: {str(e)}", stream_type=streamtype)
                button = stream_markup(chat_id)
                if videoid == "telegram":
                    ke = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
                    run = await app.send_message(
                        chat_id=original_chat_id,
                        text=ke.format(config.SUPPORT_CHAT, title[:30], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                        disable_web_page_preview=True
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    ke = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
                    run = await app.send_message(
                        chat_id=original_chat_id,
                        text=ke.format(config.SUPPORT_CHAT, title[:30], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                        disable_web_page_preview=True
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    ke = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
                    run = await app.send_message(
                        chat_id=original_chat_id,
                        text=ke.format(
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            title[:30],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                        disable_web_page_preview=True
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"
        except StreamError as e:
            await app.send_message(
                original_chat_id,
                text=f"Failed to switch stream: {str(e)}. Do /skip to change the track again.",
                disable_web_page_preview=True
            )
        except Exception as e:
            raise StreamError(f"Unexpected error in play: {str(e)}", stream_type=streamtype)

    async def start(self):
        logging.info("Starting Session Accounts For Assistance.\n")
        try:
            if config.STRING1:
                await self.one.start()
            if config.STRING2:
                await self.two.start()
            if config.STRING3:
                await self.three.start()
            if config.STRING4:
                await self.four.start()
            if config.STRING5:
                await self.five.start()
        except Exception as e:
            raise ConfigError(f"Failed to start userbots: {str(e)}")

    async def decorators(self):
        @self.one.on_update(filters.chat_update(ChatUpdate.Status.KICKED))
        @self.two.on_update(filters.chat_update(ChatUpdate.Status.KICKED))
        @self.three.on_update(filters.chat_update(ChatUpdate.Status.KICKED))
        @self.four.on_update(filters.chat_update(ChatUpdate.Status.KICKED))
        @self.five.on_update(filters.chat_update(ChatUpdate.Status.KICKED))
        @self.one.on_update(filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.two.on_update(filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.three.on_update(filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.four.on_update(filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.five.on_update(filters.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.one.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.two.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.three.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.four.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        @self.five.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))
        async def stream_services_handler(_, update: Update):
            try:
                await self.stop_stream(update.chat_id)
            except Exception as e:
                await self.log_error(update.chat_id, "stream_services_handler", e)

        @self.one.on_update(filters.stream_end)
        @self.two.on_update(filters.stream_end)
        @self.three.on_update(filters.stream_end)
        @self.four.on_update(filters.stream_end)
        @self.five.on_update(filters.stream_end)
        async def stream_end_handler(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            try:
                await self.play(client, update.chat_id)
            except Exception as e:
                raise StreamError(f"Failed to handle stream endup: {str(e)}", stream_type="audio")


BillaMusic = Call()
