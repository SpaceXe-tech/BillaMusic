# BillaMusic/utils/stream/stream.py
import os
from typing import Union
import logging

from pyrogram.types import InlineKeyboardMarkup

import config
from BillaMusic import YouTube, app
from BillaMusic.core.call import Billa
from BillaMusic.misc import db
from BillaMusic.utils.database import add_active_video_chat, is_active_chat
from BillaMusic.utils.exceptions import StreamError, DownloadError, VoiceChatError
from BillaMusic.utils.inline import aq_markup, close_markup, stream_markup
from BillaMusic.utils.pastebin import paste
from BillaMusic.utils.stream.queue import put_queue, put_queue_index


async def stream(
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        raise StreamError("No stream results provided.", stream_type=streamtype)
    if forceplay:
        try:
            await Billa.force_stop_stream(chat_id)
        except VoiceChatError as e:
            await app.send_message(
                chat_id=original_chat_id,
                text=f"Failed to force stop stream: {str(e)}",
                disable_web_page_preview=True
            )
            return
    if streamtype == "playlist":
        msg = "Queued Playlist:\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    vidid,
                ) = await YouTube.details(search, not spotify)
            except Exception as e:
                logging.error(f"Failed to fetch playlist details: {str(e)}")
                continue
            if str(duration_min) == "None":
                continue
            if duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                check = db.get(chat_id)
                if len(check) > config.QUEUE_LIMIT:
                    raise StreamError(
                        f"Queue limit reached ({config.QUEUE_LIMIT} songs). Wait for songs to finish or use /end.",
                        stream_type="playlist"
                    )
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"Queued Position: {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=status, videoid=True
                    )
                except Exception as e:
                    logging.error(f"Download failed: {str(e)}")
                    raise DownloadError(f"Failed to download track: {str(e)}", url=vidid)
                try:
                    await BillaMusic.join_call(
                        chat_id,
                        original_chat_id,
                        file_path,
                        video=status,
                    )
                except VoiceChatError as e:
                    await app.send_message(
                        chat_id=original_chat_id,
                        text=f"Failed to join call: {str(e)}",
                        disable_web_page_preview=True
                    )
                    return
                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                    forceplay=forceplay,
                )
                button = stream_markup(chat_id)
                meow = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
                run = await app.send_message(
                    original_chat_id,
                    text=meow.format(
                        f"https://t.me/{app.username}?start=info_{vidid}",
                        title[:30],
                        duration_min,
                        user_name,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    disable_web_page_preview=True
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        if count == 0:
            raise StreamError("No valid tracks found in playlist.", stream_type="playlist")
        link = await paste(msg)
        lines = msg.count("\n")
        car = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
        upl = close_markup()
        cv = "Added {} tracks to queue.\n\n<b>Check:</b> <a href={}>Click here</a>"
        await app.send_message(
            original_chat_id,
            text=cv.format(count, link),
            reply_markup=upl,
        )
        return
    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        status = True if video else None
        try:
            file_path, direct = await YouTube.download(
                vidid, mystic, videoid=True, video=status
            )
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            raise DownloadError(f"Failed to download track: {str(e)}", url=vidid)
        if await is_active_chat(chat_id):
            check = db.get(chat_id)
            if len(check) > config.QUEUE_LIMIT:
                raise StreamError(
                    f"Queue limit reached ({config.QUEUE_LIMIT} songs). Wait for songs to finish or use /end.",
                    stream_type="youtube"
                )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(chat_id)
            zn = "<b>Added to queue at #{}\n\nTitle:</b> {}\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
            await app.send_message(
                chat_id=original_chat_id,
                text=zn.format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            try:
                await Billa.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                )
            except VoiceChatError as e:
                await app.send_message(
                    chat_id=original_chat_id,
                    text=f"Failed to join call: {str(e)}",
                    disable_web_page_preview=True
                )
                return
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            button = stream_markup(chat_id)
            meo = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
            run = await app.send_message(
                original_chat_id,
                text=meo.format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:30],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(button),
                disable_web_page_preview=True
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        if await is_active_chat(chat_id):
            check = db.get(chat_id)
            if len(check) > config.QUEUE_LIMIT:
                raise StreamError(
                    f"Queue limit reached ({config.QUEUE_LIMIT} songs). Wait for songs to finish or use /end.",
                    stream_type="soundcloud"
                )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(chat_id)
            mn = "<b>Added to queue at #{}\n\nTitle:</b> {}\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
            await app.send_message(
                chat_id=original_chat_id,
                text=mn.format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            try:
                await Billa.join_call(
                    chat_id, original_chat_id, file_path, video=None
                )
            except VoiceChatError as e:
                await app.send_message(
                    chat_id=original_chat_id,
                    text=f"Failed to join call: {str(e)}",
                    disable_web_page_preview=True
                )
                return
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                forceplay=forceplay,
            )
            button = stream_markup(chat_id=chat_id)
            me = "<b>Started Streaming</b>\n\n<b>Title:</b> {}\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
            run = await app.send_message(
                chat_id=original_chat_id,
                text=me.format(title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
                disable_web_page_preview=True
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            check = db.get(chat_id)
            if len(check) > config.QUEUE_LIMIT:
                raise StreamError(
                    f"Queue limit reached ({config.QUEUE_LIMIT} songs). Wait for songs to finish or use /end.",
                    stream_type="telegram"
                )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(chat_id)
            m = "<b>Added to queue at #{}\n\nTitle:</b> {}\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
            await app.send_message(
                chat_id=original_chat_id,
                text=m.format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            try:
                await Billa.join_call(
                    chat_id, original_chat_id, file_path, video=status
                )
            except VoiceChatError as e:
                await app.send_message(
                    chat_id=original_chat_id,
                    text=f"Failed to join call: {str(e)}",
                    disable_web_page_preview=True
                )
                return
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            if video:
                await add_active_video_chat(chat_id)
            button = stream_markup(chat_id)
            mz = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {} minutes\n<b>Requested by:</b> {}"
            run = await app.send_message(
                original_chat_id,
                text=mz.format(link, title[:30], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
                disable_web_page_preview=True
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = "Live Track"
        status = True if video else None
        if await is_active_chat(chat_id):
            check = db.get(chat_id)
            if len(check) > config.QUEUE_LIMIT:
                raise StreamError(
                    f"Queue limit reached ({config.QUEUE_LIMIT} songs). Wait for songs to finish or use /end.",
                    stream_type="live"
                )
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(chat_id)
            q = "<b>Added to queue at #{}\n\nTitle:</b> {}\n<b>Duration:</b> {}\n<b>Requested by:</b> {}"
            await app.send_message(
                chat_id=original_chat_id,
                text=q.format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise StreamError("No live YouTube video found.", stream_type="live")
            try:
                await Billa.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                )
            except VoiceChatError as e:
                await app.send_message(
                    chat_id=original_chat_id,
                    text=f"Failed to join call: {str(e)}",
                    disable_web_page_preview=True
                )
                return
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            button = stream_markup(chat_id)
            az = "<b>Started Streaming</b>\n\n<b>Title:</b> <a href={}>{}</a>\n<b>Duration:</b> {}\n<b>Requested by:</b> {}"
            run = await app.send_message(
                original_chat_id,
                text=az.format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:30],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(button),
                disable_web_page_preview=True
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif streamtype == "index":
        link = result
        title = "Index or M3U8 Links"
        duration_min = "00:00"
        if await is_active_chat(chat_id):
            check = db.get(chat_id)
            if len(check) > config.QUEUE_LIMIT:
                raise StreamError(
                    f"Queue limit reached ({config.QUEUE_LIMIT} songs). Wait for songs to finish or use /end.",
                    stream_type="index"
                )
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(chat_id)
            mb = "<b>Added to queue at #{}\n\nTitle:</b> {}\n<b>Duration:</b> {}\n<b>Requested by:</b> {}"
            await mystic.edit_text(
                text=mb.format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            try:
                await Billa.join_call(
                    chat_id,
                    original_chat_id,
                    link,
                    video=True if video else None,
                )
            except VoiceChatError as e:
                await app.send_message(
                    chat_id=original_chat_id,
                    text=f"Failed to join call: {str(e)}",
                    disable_web_page_preview=True
                )
                return
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            button = stream_markup(chat_id)
            xc = "<b>Started Streaming</b>\n\n<b>Stream Type:</b> Live Stream [URL]\n<b>Requested by:</b> {}"
            run = await app.send_message(
                original_chat_id,
                text=xc.format(user_name),
                reply_markup=InlineKeyboardMarkup(button),
                disable_web_page_preview=True
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await mystic.delete()
