import asyncio
from pyrogram import Client
from pyrogram.enums import ChatType
from config import API_ID, API_HASH, SESSION_STRING
from database import save_file

user_app = None

if SESSION_STRING:
    user_app = Client(
        "userbot_session",
        api_id=int(API_ID),
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )

async def start_userbot_service():
    if not user_app:
        return False
    if not user_app.is_connected:
        try:
            await user_app.start()
            print("✅ Userbot connected for background indexing!")
            return True
        except Exception as e:
            print(f"❌ Userbot connection error: {e}")
            return False
    return True

async def index_groups_background():
    """סריקה בטוחה של הודעות אחרונות בקבוצות ושמירה ב-DB"""
    if not await start_userbot_service():
        return

    print("🔄 Starting background indexing...")
    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                try:
                    # סריקת 20 ההודעות האחרונות מכל קבוצה ברוגע
                    async for msg in user_app.get_chat_history(chat.id, limit=20):
                        if msg.text or msg.caption:
                            text = msg.text or msg.caption
                            link = msg.link or f"https://t.me/c/{str(chat.id)[4:]}/{msg.id}"
                            await save_file(text, chat.id, msg.id, link)
                    await asyncio.sleep(1)  # השהיה של שנייה בין קבוצה לקבוצה לבטיחות מלאה
                except Exception:
                    continue
        print("✅ Background indexing finished successfully!")
    except Exception as e:
        print(f"❌ Indexing error: {e}")