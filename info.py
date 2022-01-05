import re
from os import environ
from motor.motor_asyncio import AsyncIOMotorClient

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = 10786281
API_HASH = '5f42bc5562f6a1eb8bae8b77617186a0'
BOT_TOKEN ='2136703772:AAH7YT8ngkmRmsSgU8BUX1zjQT8hw8JVdyE'

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))

# Admins, Channels & Users
ADMINS = [859704527]
CHANNELS = -1001609087881
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else auth_channel
AUTH_GROUPS = [int(admin) for admin in environ.get("AUTH_GROUPS", "").split()]

# MongoDB information
client = AsyncIOMotorClient('mongodb+srv://swahilihit:swahilihit@cluster0.3nfk1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
DB2 = client['swahilihit']
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_file')

# Messages
default_start_msg = """
**Hi,Mimi ni robot niite swahili robot**
Unaweza ukapata movie ,series ,miziki ,vichekesho na huduma nyingine kibao\n
Kupata vyote hivi ni add kwenye group au chagua kwenye group zetu kwa kubonyeza button ya group zetu kisha chagua upendalo.\n
Nb.mimi natumika kwenye magroup tu nje ya hapo siwez kufanya kazi utaniona kama boshen tu
Ofa zipo mbili kwa atakaye ni  add kwenye group ya kwanza ntaongeza group lako kwenye list yangu
Ya pili ni  baada ya kuniunga utaiona we mwenyewe hii ni  siri baina yangu na admin.\n
**Karibun sana Swahili group**
"""
START_MSG = environ.get('START_MSG', default_start_msg)

BUTTON = environ.get("BUTTON",False)
FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "")
OMDB_API_KEY = environ.get("OMDB_API_KEY", "")
if FILE_CAPTION.strip() == "":
    CUSTOM_FILE_CAPTION=None
else:
    CUSTOM_FILE_CAPTION=FILE_CAPTION
if OMDB_API_KEY.strip() == "":
    API_KEY=None
else:
    API_KEY=OMDB_API_KEY
