import asyncio
from pyrogram import Client
from pyrogram.enums import ChatType
from config import API_ID, API_HASH, SESSION_STRING

GROUP_SETTINGS = {}
user_app = None

if SESSION_STRING:
    user_app = Client(
        "userbot_session",
        api_id=int(API_ID),
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )
else:
    print("⚠️ WARNING: SESSION_STRING missing in config!")

async def start_userbot_service():
    """הפעלה חד פעמית של ה-Userbot בעליית השרת"""
    if not user_app:
        print("❌ Userbot not configured (missing SESSION_STRING).")
        return False
    if not user_app.is_connected:
        try:
            await user_app.start()
            print("✅ Userbot successfully started and connected!")
            return True
        except Exception as e:
            print(f"❌ Userbot start error: {e}")
            return False
    return True

async def get_all_user_chats():
    """שליפת כל הקבוצות והערוצים בחשבון"""
    chats = []
    if not user_app or not user_app.is_connected:
        started = await start_userbot_service()
        if not started:
            return chats

    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                chats.append(chat)
                if chat.id not in GROUP_SETTINGS:
                    GROUP_SETTINGS[chat.id] = True
        print(f"✅ Found {len(chats)} chats for Userbot.")
    except Exception as e:
        print(f"❌ Error getting dialogs: {e}")
    return chats

async def search_in_telegram_groups(query):
    """חיפוש בלייב בקבוצות ובערוצים הפעילים"""
    results = []
    if not user_app or not user_app.is_connected:
        started = await start_userbot_service()
        if not started:
            return results

    try:
        chats = await get_all_user_chats()
        for chat in chats:
            chat_id = chat.id
            if not GROUP_SETTINGS.get(chat_id, True):
                continue

            try:
                async for message in user_app.search_messages(chat_id, query=query, limit=3):
                    if message.media or message.text:
                        results.append(message)
                await asyncio.sleep(0.1)
            except Exception:
                continue
    except Exception as e:
        print(f"❌ Error searching in groups: {e}")
    return results