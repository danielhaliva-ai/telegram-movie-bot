import certifi
import motor.motor_asyncio
from config import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True
)

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
    """חיפוש גמיש ב-MongoDB ללא תלות באותיות קטנות/גדולות"""
    clean_query = query.strip()
    cursor = files_collection.find(
        {"file_name": {"$regex": clean_query, "$options": "i"}}
    ).limit(10)
    results = await cursor.to_list(length=10)
    print(f"🔍 DB Search for '{clean_query}' returned {len(results)} items")
    return results