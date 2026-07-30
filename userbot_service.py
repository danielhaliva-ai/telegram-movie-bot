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
        print("❌ Userbot missing SESSION_STRING")
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
    """סריקה מקיפה ובטוחה של הקבוצות והערוצים בחשבון"""
    if not await start_userbot_service():
        return

    print("🔄 Starting full group indexing to MongoDB...")
    total_saved = 0
    
    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            # תמיכה בקבוצות, סופר-קבוצות וערוצים
            if str(chat.type) in ["ChatType.GROUP", "ChatType.SUPERGROUP", "ChatType.CHANNEL", "group", "supergroup", "channel"]:
                print(f"📂 Indexing group/channel: {chat.title} ({chat.id})")
                try:
                    # סריקת 50 ההודעות האחרונות מכל קבוצה
                    async for msg in user_app.get_chat_history(chat.id, limit=50):
                        content_text = msg.text or msg.caption
                        
                        # אם יש שם של קובץ/מדיה ללא טקסט - נחלץ את שם הקובץ
                        if not content_text:
                            if msg.document:
                                content_text = msg.document.file_name
                            elif msg.video:
                                content_text = msg.video.file_name
                        
                        if content_text:
                            # במידה ואין קישור ישיר, נבנה קישור ערוץ/קבוצה
                            link = msg.link or f"https://t.me/c/{str(chat.id).replace('-100', '')}/{msg.id}"
                            await save_file(content_text, chat.id, msg.id, link)
                            total_saved += 1
                            
                    await asyncio.sleep(1) # השהיה בטוחה בין קבוצות
                except Exception as group_err:
                    print(f"⚠️ Could not index {chat.title}: {group_err}")
                    continue
                    
        print(f"✅ Background indexing finished! Total files saved to DB: {total_saved}")
    except Exception as e:
        print(f"❌ Indexing loop error: {e}")