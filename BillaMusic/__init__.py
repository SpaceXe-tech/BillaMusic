from BillaMusic.core.bot import Billa
from BillaMusic.core.dir import dirr
from BillaMusic.core.userbot import Userbot
from BillaMusic.misc import dbb

dirr()
dbb()

app = Billa()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
