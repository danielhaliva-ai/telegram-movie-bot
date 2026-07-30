import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from userbot_service import start_userbot_service, index_groups_background

bot = Client(
    "movie_search_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Tj_Bots")
)

async def main():
    print("🚀 Starting Userbot...")
    await start_userbot_service()
    
    print("🚀 Starting Main Bot...")
    await bot.start()
    
    # הפעלת האינדוקס ברקע באופן שאינו חוסם
    asyncio.create_task(index_groups_background())
    
    print("✅ Bot is online and running safely!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())