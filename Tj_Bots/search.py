import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from userbot_service import search_in_telegram_groups

# מילון לשמירת משתמשים מאושרים (בזיכרון)
APPROVED_USERS = set()
REQUIRE_APPROVAL = True  # האם מנגנון האישורים פעיל

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "admin", "auth", "clearchat"]))
async def search_handler(client: Client, message: Message):
    user_id = message.from_user.id

    # בדיקה אם המשתמש מאושר (אם המנגנון פעיל)
    if REQUIRE_APPROVAL and user_id not in APPROVED_USERS:
        return await message.reply("🔒 **הבוט נעול.** עליך להמתין לאישור מנהל כדי להשתמש בחיפוש.", quote=True)

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

    # חיפוש בלייב בקבוצות דרך ה-Userbot
    live_results = await search_in_telegram_groups(query)

    if not live_results:
        txt = f"❌ **לא נמצאו תוצאות עבור:** `{query}`"
        if status_msg:
            try:
                await status_msg.edit_text(txt)
            except Exception:
                await message.reply(txt, quote=True)
        else:
            await message.reply(txt, quote=True)
        return

    # הרכבת תוצאות החיפוש
    response_text = f"🔎 **תוצאות חיפוש עבור:** `{query}`\n"
    response_text += f"📌 **נמצאו:** {len(live_results)} תוצאות\n\n"

    buttons = []
    for msg in live_results[:10]:
        chat_title = msg.chat.title if msg.chat else "קבוצה"
        link = msg.link if msg.link else "https://t.me"
        snippet = msg.text[:35] if msg.text else "קובץ/מדיה"
        buttons.append([InlineKeyboardButton(f"🎬 {chat_title}: {snippet}", url=link)])

    markup = InlineKeyboardMarkup(buttons)

    if status_msg:
        try:
            await status_msg.edit_text(response_text, reply_markup=markup, disable_web_page_preview=True)
        except Exception:
            await message.reply(response_text, reply_markup=markup, disable_web_page_preview=True, quote=True)
    else:
        await message.reply(response_text, reply_markup=markup, disable_web_page_preview=True, quote=True)