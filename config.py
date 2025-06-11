# This file contains all the config variables that are needed to run the Billa Music Bot


MONGO_DB_URI = "mongodb://username:pwd@localhost:27017/dbname" # mongodb url for database
DURATION_LIMIT_MIN = 99999 # minimum duration limit for the song in minutes
LOGGER_ID = LOGGER_ID = int(getenv("LOGGER_ID", None)) # channel id of telegram to keep logs
OWNER_ID = int(getenv("OWNER_ID", 5960968099))3 # your telegram user id
SUPPORT_CHANNEL = "https://t.me/BillaSpace" # your telegram channel link to post updates about the bot
SUPPORT_CHAT = "https://t.me/BillaCore" # your telegram group link to discuss about the bot
AUTO_LEAVING_ASSISTANT = True # True if you want your music assistant account to leave group chats after playing the song, helpful in cleaning the reduntant group chats from assistant account
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "95f4f5c6df5744698035a0948e801ad9") # get from spotify api if you want this bot to use spotify as it's play source
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "4b03167b38c943c3857333b3f5ea95ea") # get from spotify api if you want this bot to use spotify as it's play source
PLAYLIST_FETCH_LIMIT = 350 # number of maximum songs bot can play from a playlist
TG_AUDIO_FILESIZE_LIMIT = 104857600 # audio file size limit  to upload/download in bytes
TG_VIDEO_FILESIZE_LIMIT = 4294967296 # video file size limit to upload/download in bytes
QUEUE_LIMIT = 200 # number of maximum songs that can be put inside a queue
STRING1 = "BQFzpC0AnvzoAAAAGnnH-cAA" # your account's pyrogram v2 string session, get from any string session bot generator or checkout replit
# optional string sessions if you want to use multiple assistant accounts
STRING2 = None
STRING3 = None
STRING4 = None
STRING5 = None
API_ID = 24620300 # your account's api id from api.telegram.org
API_HASH = "9a098f01aa56c836f2e34aee4b7ef963" # your account's api hash from api.telegram.org
BOT_TOKEN = "29109320:9dnnwsk" # your bot's api token from @BotFather
BOT_ID = 219810 # your bot's user id
BOT_USERNAME = "Billamusic_bot" # your bot's username
BOT_NAME = "BillaMusic" # your bot's name

adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
