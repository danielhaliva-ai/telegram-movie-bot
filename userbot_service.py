import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING

# מילון לשמירת מצב הקבוצות (קבוצה מופעלת/מופסקת)
# ברירת מחדל: True (כל הקבוצות פעילות)
GROUP_SETTINGS = {}

user_app = None

if SESSION_STRING:
    user_app = Client(
        "userbot_session",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )

async def safe_start_userbot():
    if not user_app:
        return False
    if not user_app.is_connected:
        try:
            await user_app.start()
            return True
        except Exception as e:
            print(f"Userbot Connection Error: {e}")
            return False
    return True

async def get_all_user_chats():
    """שליפת כל הקבוצות שהחשבון מחובר אליהן"""
    chats = []
    if not await safe_start_userbot():
        return chats

    try:
        async for dialog in user_app.get_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                chats.append(dialog.chat)
                # אם קבוצה חדשה, נגדיר אותה כפעילה כברירת מחדל
                if dialog.chat.id not in GROUP_SETTINGS:
                    GROUP_SETTINGS[dialog.chat.id] = True
    except Exception as e:
        print(f"Error getting chats: {e}")
    return chats

async def search_in_telegram_groups(query):
    """חיפוש בטוח בקבוצות הפעילות בלבד עם הגנת Anti-Flood"""
    results = []
    if not await safe_start_userbot():
        return results

    try:
        async for dialog in user_app.get_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                chat_id = dialog.chat.id
                
                # בדיקה אם המנהל ביטל את הקבוצה הזו
                if not GROUP_SETTINGS.get(chat_id, True):
                    continue

                try:
                    # חיפוש מוגבל ל-3 קבצים לקבוצה למניעת הצפה
                    async for message in user_app.search_messages(chat_id, query=query, limit=3):
                        if message.media or message.text:
                            results.append(message)
                    
                    # השהיה קטנה לבטיחות מלאה מול שרתי טלגרם
                    await asyncio.sleep(0.2)
                except Exception:
                    continue
    except Exception as e:
        print(f"Error searching groups: {e}")
    return results