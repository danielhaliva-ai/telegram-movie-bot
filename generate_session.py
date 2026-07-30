from pyrogram import Client

# הכנס כאן את המפתחות שלך ישירות
API_ID = 12345678  # החלף במספר ה-API_ID שלך
API_HASH = "your_api_hash_here"  # החלף ב-API_HASH שלך

app = Client("userbot_gen", api_id=API_ID, api_hash=API_HASH)

with app:
    print("\n================ SESSION STRING ================\n")
    print(app.export_session_string())
    print("\n================================================\n")