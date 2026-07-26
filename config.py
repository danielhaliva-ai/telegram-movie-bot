import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", "39417638"))
API_HASH = os.environ.get("API_HASH", "b043aacc0da0ec542a9bf586513d2568")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8900460988:AAFV3cceuxkGixSypGCkbjjkwxcPx1uEGg8")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ww0527119835_db_user:vmi25IRkHGdoMudg@cluster0.lbxxpwt.mongodb.net/?appName=Cluster0")
DB_NAME = "TjBotDB"

# מנהלים
ADMINS = [8526860681]

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
UPDATE_CHANNEL = "searchgram_bots"
REQUEST_GROUP = "https://t.me/searchgram_group"

PHOTO_URL = "https://i.ibb.co/BK2j0c7p/x.jpg"

AUTH_CHANNEL_FORCE = False