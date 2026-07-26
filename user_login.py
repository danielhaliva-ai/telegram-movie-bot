import asyncio
from pyrogram import Client
from config import API_ID, API_HASH

# יצירת חיבור כמשתמש רגיל (לא בוט)
user_app = Client("User_Session", api_id=API_ID, api_hash=API_HASH)

async def main():
    async with user_app:
        me = await user_app.get_me()
        print(f"✅ התחברת בהצלחה כמשתמש: {me.first_name} (@{me.username})")

if __name__ == "__main__":
    user_app.run(main())