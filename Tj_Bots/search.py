import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from database import db
from userbot_service import search_in_telegram_groups

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "settings"]))
async def search_handler(client: Client, message: Message):
    query = message.text.strip()
    if not query or len(query) < 2:
        return await message.reply("❌ נא להזין שם סרט/סדרה של לפחות 2 אותיות.", quote=True)

    status_msg = None
    try:
        status_msg = await message.reply("🔍 **מחפש עבורך בקבוצות, רגע אחד...**", quote=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            status_msg = await message.reply("🔍 **מחפש עבורך בקבוצות, רגע אחד...**", quote=True)
        except Exception:
            pass
    except Exception:
        pass

    # 1. חיפוש במסד הנתונים הפנימי (MongoDB)
    db_results = await db.search_files(query)
    
    # 2. חיפוש בלייב בקבוצות דרך ה-Userbot
    live_results = await search_in_telegram_groups(query)

    if not db_results and not live_results:
        txt = f"❌ **לא נמצאו תוצאות עבור:** `{query}`"
        if status_msg:
            try:
                await status_msg.edit_text(txt)
            except Exception:
                await message.reply(txt, quote=True)
        else:
            await message.reply(txt, quote=True)
        return

    # הרכבת תגובת התוצאות
    buttons = []
    
    # הוספת תוצאות מ-MongoDB
    if db_results:
        for file in db_results[:10]:
            file_name = file.get("file_name", "קובץ ללא שם")
            file_id = str(file.get("_id"))
            buttons.append([InlineKeyboardButton(f"🎬 {file_name}", callback_data=f"file_{file_id}")])

    response_text = f"🔎 **תוצאות חיפוש עבור:** `{query}`\n"
    response_text += f"📌 **נמצאו:** {len(db_results) + len(live_results)} תוצאות\n\n"

    # הוספת תוצאות טקסטואליות מתוך הקבוצות
    if live_results:
        response_text += "💬 **מתוך קבוצות טלגרם:**\n"
        for msg in live_results[:5]:
            chat_title = msg.chat.title if msg.chat else "קבוצה"
            link = msg.link if msg.link else "#"
            snippet = msg.text[:60] if msg.text else "מדיה"
            response_text += f"• [{chat_title}]({link}): {snippet}...\n"

    markup = InlineKeyboardMarkup(buttons) if buttons else None

    if status_msg:
        try:
            await status_msg.edit_text(response_text, reply_markup=markup, disable_web_page_preview=True)
        except Exception:
            await message.reply(response_text, reply_markup=markup, disable_web_page_preview=True, quote=True)
    else:
        await message.reply(response_text, reply_markup=markup, disable_web_page_preview=True, quote=True)