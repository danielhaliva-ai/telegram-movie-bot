import asyncio
from pyrogram import Client, enums
from config import API_ID, API_HASH

user_app = Client("User_Session", api_id=API_ID, api_hash=API_HASH)

# מילון לשמירת מצב הקבוצות: {chat_id: True/False}
GROUP_SETTINGS = {}

async def get_all_user_chats():
    """שולף את כל הקבוצות והערוצים שהיוזר חבר בהם"""
    if not user_app.is_connected:
        await user_app.start()
        
    chats = []
    async for dialog in user_app.get_dialogs():
        chat = dialog.chat
        if chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
            chats.append({'id': chat.id, 'title': chat.title})
            # אם הקבוצה עדיין לא קיימת בהגדרות, כברירת מחדל היא פעילה (True)
            if chat.id not in GROUP_SETTINGS:
                GROUP_SETTINGS[chat.id] = True
    return chats

async def search_in_telegram_groups(query: str):
    results = []
    
    if not user_app.is_connected:
        if not user_app.is_connected:
            await user_app.start()

    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            
            if chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
                
                # בודק אם המנהל סימן את הקבוצה הזו כפעילה (True)
                is_active = GROUP_SETTINGS.get(chat.id, True)
                if not is_active:
                    continue

                try:
                    async for msg in user_app.search_messages(chat_id=chat.id, query=query, limit=5):
                        if msg.media:
                            media_obj = msg.video or msg.document or msg.audio
                            file_name = getattr(media_obj, 'file_name', None) or msg.caption or f"File_{msg.id}"
                            msg_link = msg.link if msg.link else f"https://t.me/c/{str(chat.id).replace('-100', '')}/{msg.id}"
                            
                            results.append({
                                'chat_title': chat.title,
                                'file_name': file_name,
                                'msg_link': msg_link
                            })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error searching via Userbot: {e}")

    return results