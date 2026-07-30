import asyncio
import sys
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from userbot_service import start_userbot_service, index_groups_background

# הכרחת הדפסה מיידית ללוגים של Railway
sys.stdout.reconfigure(line_buffering=True)

print("🚀 Starting Bot Service via bot.py...", flush=True)

app = Client(
    "movie_search_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Tj_Bots")
)

async def start_bot():
    print("🤖 Starting Main Bot Client...", flush=True)
    await app.start()
    print("✅ Main Bot is Online and Listening!", flush=True)
    
    print("🚀 Triggering Background Userbot Indexer...", flush=True)
    asyncio.create_task(index_groups_background())
    
    print("🌐 Service fully initialized.", flush=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())