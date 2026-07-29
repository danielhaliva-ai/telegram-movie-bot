import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING

# הגדרת הלקוח עם זיכרון זמני כדי לא לדרוס DB ישן
user_app = Client(
    "userbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING if SESSION_STRING else None,
    in_memory=True
)

GROUP_SETTINGS = {}

async def safe_start_userbot():
    """התחברות בטוחה ללא לולאות אינסופיות"""
    if not user_app.is_connected:
        try:
            await user_app.start()
            return True
        except Exception as e:
            print(f"Userbot Connection Error: {e}")
            return False
    return True

async def get_all_user_chats():
    chats = []
    if not await safe_start_userbot():
        return chats

    try:
        async for dialog in user_app.get_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                chats.append(dialog.chat)
    except Exception as e:
        print(f"Error getting chats: {e}")
    return chats

async def search_in_telegram_groups(query):
    results = []
    if not await safe_start_userbot():
        return results

    try:
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