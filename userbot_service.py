import asyncio
from pyrogram import Client
from pyrogram.enums import ChatType
from config import API_ID, API_HASH, SESSION_STRING

GROUP_SETTINGS = {}

def get_userbot_client():
    if not SESSION_STRING:
        print("⚠️ SESSION_STRING missing in config!")
        return None
    return Client(
        "userbot_session",
        api_id=int(API_ID),
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )

async def get_all_user_chats():
    """שליפת כל הקבוצות והערוצים בחשבון"""
    chats = []
    app = get_userbot_client()
    if not app:
        return chats

    try:
        async with app:
            async for dialog in app.get_dialogs():
                chat = dialog.chat
                # בדיקה אם מדובר בקבוצה, סופר-קבוצה או ערוץ
                if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                    chats.append(chat)
                    if chat.id not in GROUP_SETTINGS:
                        GROUP_SETTINGS[chat.id] = True
        print(f"✅ Userbot found {len(chats)} active chats/groups.")
    except Exception as e:
        print(f"❌ Error fetching dialogs: {e}")
    return chats

async def search_in_telegram_groups(query):
    """חיפוש בלייב בקבוצות ובערוצים הפעילים"""
    results = []
    app = get_userbot_client()
    if not app:
        return results

    try:
        async with app:
            # נביא את הדיאלוגים
            async for dialog in app.get_dialogs():
                chat = dialog.chat
                if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                    # בדיקה אם הקבוצה פעילה בהגדרות המנהל
                    if not GROUP_SETTINGS.get(chat.id, True):
                        continue
                    
                    try:
                        async for message in app.search_messages(chat.id, query=query, limit=3):
                            if message.media or message.text:
                                results.append(message)
                        await asyncio.sleep(0.1)
                    except Exception:
                        continue
    except Exception as e:
        print(f"❌ Error searching in groups: {e}")
    return results