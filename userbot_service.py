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
else:
    print("❌ Critical: SESSION_STRING is missing in Environment Variables!")

async def start_userbot_service():
    if not user_app:
        print("❌ Userbot client is not initialized.")
        return False
    if not user_app.is_connected:
        try:
            print("🔄 Connecting Userbot to Telegram...")
            await user_app.start()
            print("✅ Userbot connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Userbot failed to connect: {e}")
            return False
    return True

async def index_groups_background():
    """סריקה מלאה של קבוצות וערוצים ברקע עם לוגים מפורטים"""
    print("🚀 Initiating background indexing task...")
    
    connected = await start_userbot_service()
    if not connected:
        print("❌ Indexing aborted: Userbot is not connected.")
        return

    print("🔄 Fetching user dialogs/groups...")
    total_saved = 0

    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            chat_type_str = str(chat.type)
            
            # בדיקת סוג הצ'אט (קבוצות, סופר-קבוצות וערוצים)
            if any(t in chat_type_str for t in ["GROUP", "SUPERGROUP", "CHANNEL", "group", "supergroup", "channel"]):
                print(f"📂 Processing Chat: '{chat.title}' (ID: {chat.id})")
                try:
                    async for msg in user_app.get_chat_history(chat.id, limit=50):
                        text_content = msg.text or msg.caption
                        
                        if not text_content:
                            if msg.document:
                                text_content = msg.document.file_name
                            elif msg.video:
                                text_content = msg.video.file_name

                        if text_content:
                            clean_link = msg.link or f"https://t.me/c/{str(chat.id).replace('-100', '')}/{msg.id}"
                            await save_file(text_content, chat.id, msg.id, clean_link)
                            total_saved += 1
                            
                    print(f"✅ Finished chat '{chat.title}'. Total saved so far: {total_saved}")
                    await asyncio.sleep(1)
                except Exception as group_err:
                    print(f"⚠️ Error reading history for '{chat.title}': {group_err}")
                    continue

        print(f"🎉 All groups indexed successfully! Total entries saved in MongoDB: {total_saved}")
    except Exception as e:
        print(f"❌ Fatal error during indexing loop: {e}")