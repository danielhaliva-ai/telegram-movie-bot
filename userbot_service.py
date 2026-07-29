import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING

user_app = Client(
    "userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

GROUP_SETTINGS = {}

async def get_all_user_chats():
    chats = []
    try:
        if not user_app.is_connected:
            await user_app.start()
        async for dialog in user_app.get_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                chats.append(dialog.chat)
    except Exception as e:
        print(f"Error getting chats: {e}")
    return chats

async def search_in_telegram_groups(query):
    results = []
    try:
        if not user_app.is_connected:
            await user_app.start()
        
        async for dialog in user_app.get_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                try:
                    async for message in user_app.search_messages(dialog.chat.id, query=query, limit=5):
                        if message.media:
                            results.append(message)
                except Exception:
                    continue
    except Exception as e:
        print(f"Error searching groups: {e}")
    return results