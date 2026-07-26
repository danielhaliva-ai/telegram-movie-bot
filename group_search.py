import asyncio
from pyrogram import Client, enums
from config import API_ID, API_HASH

# יצירת לולאה ייעודית למניעת התנגשויות ב-Python 3.14
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

user_app = Client("User_Session", api_id=API_ID, api_hash=API_HASH)

async def search_movie_in_groups(query: str):
    print(f"🔍 מתחיל חיפוש עבור: '{query}'...")
    results = []
    
    async with user_app:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            
            # מסננים קבוצות וערוצים בלבד
            if chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
                try:
                    async for msg in user_app.search_messages(chat_id=chat.id, query=query, limit=5):
                        if msg.media:
                            media_obj = msg.video or msg.document or msg.audio
                            file_name = getattr(media_obj, 'file_name', None) or msg.caption or f"File_{msg.id}"
                            file_id = getattr(media_obj, 'file_id', None)
                            
                            results.append({
                                'chat_title': chat.title,
                                'chat_id': chat.id,
                                'message_id': msg.id,
                                'file_name': file_name,
                                'file_id': file_id
                            })
                except Exception:
                    continue

    return results

async def main():
    search_term = input("הכנס שם של סרט לחיפוש: ")
    found_files = await search_movie_in_groups(search_term)
    
    print(f"\n📊 נמצאו {len(found_files)} תוצאות:")
    for item in found_files:
        print(f"🎬 [מתוך: {item['chat_title']}] - {item['file_name']}")

if __name__ == "__main__":
    # הרצה דרך הלולאה שהגדרנו מראש
    loop.run_until_complete(main())