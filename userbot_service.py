import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING
from database import save_file, register_or_update_group

user_app = None

clean_session = SESSION_STRING.strip() if SESSION_STRING else None

if clean_session:
    user_app = Client(
        "userbot_session",
        api_id=int(API_ID),
        api_hash=API_HASH,
        session_string=clean_session,
        in_memory=True
    )

async def start_userbot_service():
    if not user_app:
        print("❌ Userbot client missing", flush=True)
        return False
    if not user_app.is_connected:
        try:
            await user_app.start()
            print("✅ Userbot connected!", flush=True)
            return True
        except Exception as e:
            print(f"❌ Userbot connection error: {e}", flush=True)
            return False
    return True

async def index_groups_background():
    """סריקת קבוצות ברקע ורישומן במסד הנתונים"""
    print("🚀 Initiating background indexing...", flush=True)
    if not await start_userbot_service():
        return

    total_saved = 0
    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            chat_type_str = str(chat.type)
            
            if any(t in chat_type_str for t in ["GROUP", "SUPERGROUP", "CHANNEL", "group", "supergroup", "channel"]):
                print(f"📂 Processing Chat: '{chat.title}' ({chat.id})", flush=True)
                # רישום הקבוצה במסד הנתונים
                await register_or_update_group(chat.id, chat.title)
                
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
                            
                    await asyncio.sleep(1)
                except Exception as group_err:
                    print(f"⚠️ Error in '{chat.title}': {group_err}", flush=True)
                    continue

        print(f"🎉 Indexing completed! Total saved: {total_saved}", flush=True)
    except Exception as e:
        print(f"❌ Indexing loop error: {e}", flush=True)