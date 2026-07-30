import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database import search_files

APPROVED_USERS = set()
REQUIRE_APPROVAL = True

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "admin", "auth", "clearchat"]))
async def search_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if REQUIRE_APPROVAL and user_id not in APPROVED_USERS:
        return await message.reply("🔒 **הבוט נעול.** עליך להמתין לאישור מנהל כדי להשתמש בחיפוש.", quote=True)

    query = message.text.strip()
    if not query or len(query) < 2:
        return await message.reply("❌ נא להזין שם סרט/סדרה של לפחות 2 אותיות.", quote=True)

    status_msg = await message.reply("🔍 **מחפש במסד הנתונים...**", quote=True)

    # חיפוש מהיר ב-DB בלבד (ללא פנייה לטלגרם)
    db_results = await search_files(query)

    if not db_results:
        return await status_msg.edit_text(f"❌ **לא נמצאו תוצאות עבור:** `{query}`")

    response_text = f"🔎 **תוצאות חיפוש עבור:** `{query}`\n📌 **נמצאו:** {len(db_results)} תוצאות\n\n"
    
    buttons = []
    for item in db_results:
        title = item["file_name"][:35]
        link = item["file_link"]
        buttons.append([InlineKeyboardButton(f"🎬 {title}", url=link)])

    await status_msg.edit_text(response_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)