import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from userbot_service import start_userbot_service

# הגדרת הבוט הראשי
bot = Client(
    "movie_search_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Tj_Bots")
)

async def main():
    print("🚀 Starting Userbot service...")
    await start_userbot_service()
    
    print("🚀 Starting Main Bot...")
    await bot.start()
    
    print("✅ Bot is online and running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())