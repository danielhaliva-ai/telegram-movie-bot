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
settings_collection = db["settings"]
groups_collection = db["groups"]

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
    """חיפוש גמיש ב-MongoDB רק בקבוצות שמאושרות להצגה"""
    # שליפת רשימת הקבוצות המושבתות
    disabled_groups = await groups_collection.distinct("chat_id", {"enabled": False})
    
    clean_query = query.strip()
    filter_query = {
        "file_name": {"$regex": clean_query, "$options": "i"},
        "chat_id": {"$nin": disabled_groups}  # סינון קבוצות מבוטלות
    }
    
    cursor = files_collection.find(filter_query).limit(10)
    results = await cursor.to_list(length=10)
    return results

# --- ניהול הגדרות מנהל ---

async def set_start_photo(photo_id):
    """עדכון מזהה תמונת הברכה"""
    await settings_collection.update_one(
        {"key": "start_photo"},
        {"$set": {"value": photo_id}},
        upsert=True
    )

async def get_start_photo():
    """שליפת תמונת הברכה הנוכחית"""
    doc = await settings_collection.find_one({"key": "start_photo"})
    return doc["value"] if doc else None

async def register_or_update_group(chat_id, title, enabled=True):
    """רישום או עדכון סטטוס קבוצה"""
    await groups_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"title": title}, "$setOnInsert": {"enabled": enabled}},
        upsert=True
    )

async def toggle_group_status(chat_id):
    """שינוי סטטוס קבוצה (פעיל/מבוטל)"""
    group = await groups_collection.find_one({"chat_id": chat_id})
    if group:
        new_status = not group.get("enabled", True)
        await groups_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": new_status}}
        )
        return new_status
    return True

async def get_all_groups():
    """שליפת כל הקבוצות והסטטוס שלהן"""
    cursor = groups_collection.find({})
    return await cursor.to_list(length=100)