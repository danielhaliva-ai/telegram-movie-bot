import motor.motor_asyncio
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.users = self.db.users
        self.files = self.db.files

    # --- מנגנון משתמשים ---
    async def add_user(self, user_id, name):
        user = await self.users.find_one({"_id": user_id})
        if not user:
            await self.users.insert_one({"_id": user_id, "name": name})

    async def is_user_exist(self, user_id):
        user = await self.users.find_one({"_id": user_id})
        return bool(user)

    # --- מנגנון קבצים וחיפוש ---
    async def search_files(self, query):
        results = []
        try:
            # חיפוש לפי שם הקובץ (לא רגיש לאותיות גדולות/קטנות)
            cursor = self.files.find({"file_name": {"$regex": query, "$options": "i"}})
            async for doc in cursor:
                results.append(doc)
        except Exception as e:
            print(f"Database search error: {e}")
        return results

    async def get_file(self, file_id):
        try:
            from bson.objectid import ObjectId
            return await self.files.find_one({"_id": ObjectId(file_id)})
        except Exception:
            return await self.files.find_one({"_id": file_id})

    async def save_file(self, file_data):
        try:
            result = await self.files.insert_one(file_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

db = Database()