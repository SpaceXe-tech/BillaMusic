from BillaMusic.core.bot import BillaMusic
from BillaMusic.core.dir import dirr
from BillaMusic.core.userbot import Userbot
from BillaMusic.misc import dbb

dirr()
dbb()

app = BillaMusic()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
