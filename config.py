import re
from os import getenv

from dotenv import load_dotenv

load_dotenv()

# This file contains all the config variables that are needed to run the Billa Music Bot

API_ID = 24620300 # your account's api id from api.telegram.org
API_HASH = "9a098f01aa56c836f2e34aee4b7ef963" # your account's api hash from api.telegram.org
BOT_TOKEN = getenv("BOT_TOKEN") # your bot's api token from @BotFather
BOT_ID = int(getenv("BOT_ID", None))# your bot's user id
BOT_USERNAME = "billamusic_bot" # your bot's username
BOT_NAME = "BillaMusic" # your bot's name


MONGO_DB_URI = getenv("MONGO_DB_URI") # mongodb url for database

DURATION_LIMIT_MIN = 99999 # minimum duration limit for the song in minutes

LOGGER_ID = LOGGER_ID = int(getenv("LOGGER_ID", None)) # channel id of telegram to keep logs
OWNER_ID = int(getenv("OWNER_ID", 5960968099)) # your telegram user id

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/BillaSpace")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/BillaCore")

# Set True if you want your music assistant account to leave group chats after playing the song, helpful in cleaning the reduntant group chats from assistant account
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))


SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "95f4f5c6df5744698035a0948e801ad9") # get from spotify api if you want this bot to use spotify as it's play source
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "4b03167b38c943c3857333b3f5ea95ea") # get from spotify api if you want this bot to use spotify as it's play source
PLAYLIST_FETCH_LIMIT = 350 # number of maximum songs bot can play from a playlist

TG_AUDIO_FILESIZE_LIMIT = 104857600 # audio file size limit  to upload/download in bytes
TG_VIDEO_FILESIZE_LIMIT = 4294967296 # video file size limit to upload/download in bytes
QUEUE_LIMIT = 200 # number of maximum songs that can be put inside a queue

STRING1 = getenv("STRING_SESSION1", None) # your account's pyrogram v2 string session, get from any string session bot generator or checkout replit
# optional string sessions if you want to use multiple assistant accounts
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
