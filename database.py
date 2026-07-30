import motor.motor_asyncio
from config import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["movie_bot_db"]
files_collection = db["files"]

async def save_file(file_name, chat_id, message_id, file_link):
    """שמירת קובץ/סרט במסד הנתונים"""
    doc = {
        "file_name": file_name,
        "chat_id": chat_id,
        "message_id": message_id,
        "file_link": file_link
    }
    await files_collection.update_one(
        {"file_link": file_link},
        {"$set": doc},
        upsert=True
    )

async def search_files(query):
    """חיפוש מהיר ובטוח בתוך מסד הנתונים"""
    cursor = files_collection.find(
        {"file_name": {"$regex": query, "$options": "i"}}
    ).limit(10)
    return await cursor.to_list(length=10)