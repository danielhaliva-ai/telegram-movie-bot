import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import UPDATE_CHANNEL, REQUEST_GROUP, PHOTO_URL, ADMINS, LOG_CHANNEL, AUTH_CHANNEL_FORCE
from database import db

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        await send_home_message(client, message)

async def send_home_message(client, message, user=None, is_edit=False):
    if not user:
        user = message.from_user
    
    user_mention = user.mention
    bot_name = client.me.first_name
    bot_username = client.me.username
    bot_mention = f"[{bot_name}](https://t.me/{bot_username})"
    
    buttons = [
        [InlineKeyboardButton("🔍 חיפוש סרט", callback_data="btn_search"), InlineKeyboardButton("🔥 פופולריים", callback_data="btn_trending")],
        [InlineKeyboardButton("🎲 סרט אקראי", callback_data="btn_random"), InlineKeyboardButton('〄 עזרה 〄', callback_data='help')],
        [InlineKeyboardButton('✇ קבוצת בקשות ✇', url=REQUEST_GROUP), InlineKeyboardButton('✇ ערוץ עדכונים ✇', url=f'https://t.me/{UPDATE_CHANNEL}')],
        [InlineKeyboardButton('⇋ להוספה לקבוצה ⇋', url=f"http://t.me/{client.me.username}?startgroup&admin=delete_messages")]
    ]
    
    # אם המשתמש הוא מנהל, נוסיף כפתור פאנל ניהול
    if user.id in ADMINS:
        buttons.append([InlineKeyboardButton("⚙️ פאנל מנהל", callback_data="admin_panel")])

    # כאן מעודכן השם שלך כמתכנת ראשי
    txt = (f"**היי {user_mention} 👋**\n"
           f"**ברוכים הבאים ל- {bot_mention}** 😎\n\n"
           "**אני מנוע חיפוש סרטים וסדרות חדשני,**\n"
           "<b>התפקיד שלי זה לחפש סרטים בקבוצות,\n"
           "הוסיפו אותי לקבוצה שלכם ואני אמשיך מכאן.</b> ☄️\n\n"
           f"<blockquote>**👨🏼‍💻 מתכנת ראשי: @DANIEL_HAHAH**</blockquote>")
    
    if is_edit:
        await message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_photo(PHOTO_URL, caption=txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

@Client.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_command(client, message):
    await show_admin_panel(message)

async def show_admin_panel(message, is_edit=False):
    txt = "<b>👑 פאנל ניהול ראשי</b>\n\nכאן תוכל לנהל את הבוט, לראות סטטיסטיקות ולאנדקס קבצים."
    buttons = [
        [InlineKeyboardButton("📊 סטטיסטיקות", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 הודעת תפוצה", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🏠 חזרה לבית", callback_data="home")]
    ]
    if is_edit:
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    if data == "btn_search":
        await query.answer()
        return await query.message.reply_text("פשוט רשום לי את שם הסרט או הסדרה שאתה מחפש! 🔎", quote=True)

    elif data == "btn_trending":
        await query.answer("טוען תכנים פופולריים...")
        return await query.message.reply_text("🔥 **הסרטים החמים כרגע:**\n1. פאודה\n2. מהיר ועצבני\n3. הארי פוטר", quote=True)

    elif data == "btn_random":
        await query.answer()
        return await query.message.reply_text("🎲 **המלצה אקראית עבורך:** Inception (2010)", quote=True)

    elif data == "admin_panel" and user_id in ADMINS:
        await show_admin_panel(query.message, is_edit=True)

    elif data == "admin_stats" and user_id in ADMINS:
        total_users = await db.users.count_documents({})
        total_files = await db.files.count_documents({})
        await query.answer(f"משתמשים: {total_users} | קבצים: {total_files}", show_alert=True)

    elif data == "home":
        await send_home_message(client, query.message, user=query.from_user, is_edit=True)

    elif data == "help":
        btns = [[InlineKeyboardButton('🏠 בית 🏠', callback_data='home')]]
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption="<b>מדריך עזרה לבוט חיפוש סרטים.</b>"), reply_markup=InlineKeyboardMarkup(btns))