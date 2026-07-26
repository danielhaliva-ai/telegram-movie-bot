import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from .utils import clean_filename
from userbot_service import search_in_telegram_groups, get_all_user_chats, GROUP_SETTINGS
from config import ADMINS

# הודעת פתיחה
@Client.on_message(filters.command("start"))
async def start_handler(client, message):
    text = (
        "👋 **ברוך הבא לבוט חיפוש הסרטים והסדרות!**\n\n"
        "פשוט כתוֹב לי בצ'אט את שם הסרט או הסדרה שאתה מחפש:"
    )
    
    keyboard = []
    # אם המשתמש הוא מנהל, מוסיפים לו כפתור הגדרות
    if message.from_user.id in ADMINS:
        keyboard.append([InlineKeyboardButton("⚙️ הגדרות קבוצות (למנהל)", callback_data="admin_groups_menu")])
        
    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await message.reply_text(text, reply_markup=markup, quote=True)

# פקודת הגדרות מנהל /settings
@Client.on_message(filters.command("settings") & filters.user(ADMINS))
async def settings_command_handler(client, message):
    await show_groups_settings_menu(message)

# הצגת תפריט ה-ON/OFF של הקבוצות
from pyrogram.errors import MessageNotModified

# הצגת תפריט ה-ON/OFF של הקבוצות
async def show_groups_settings_menu(message_or_query, is_edit=False):
    chats = await get_all_user_chats()
    
    keyboard = []
    for chat in chats:
        chat_id = chat['id']
        title = chat['title']
        is_active = GROUP_SETTINGS.get(chat_id, True)
        
        status_icon = "✅" if is_active else "❌"
        btn_text = f"{status_icon} {title}"
        
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_grp_{chat_id}")])

    keyboard.append([InlineKeyboardButton("🔄 רענן רשימה", callback_data="admin_groups_menu")])
    markup = InlineKeyboardMarkup(keyboard)
    
    text = "⚙️ **הגדרות קבוצות חיפוש:**\nלחץ על קבוצה כדי להפעיל (✅) או לנטרל (❌) אותה מחיפוש:"
    
    try:
        if is_edit:
            await message_or_query.edit_text(text, reply_markup=markup)
        else:
            await message_or_query.reply_text(text, reply_markup=markup)
    except MessageNotModified:
        # התעלמות משגיאה במידה וההודעה לא השתנתה
        pass
# טיפול בלחיצות על כפתורי ההגדרות וה-ON/OFF
@Client.on_callback_query()
async def callback_dispatcher(client, query: CallbackQuery):
    data = query.data
    
    # פתיחת תפריט הגדרות
    if data == "admin_groups_menu":
        if query.from_user.id not in ADMINS:
            await query.answer("⛔ אינך מנהל!", show_alert=True)
            return
        await query.answer()
        await show_groups_settings_menu(query.message, is_edit=True)
        
    # שינוי מצב קבוצה (ON / OFF)
    elif data.startswith("toggle_grp_"):
        if query.from_user.id not in ADMINS:
            await query.answer("⛔ אינך מנהל!", show_alert=True)
            return
            
        chat_id = int(data.replace("toggle_grp_", ""))
        current_status = GROUP_SETTINGS.get(chat_id, True)
        
        # הופך את המצב (מ-True ל-False או להפך)
        GROUP_SETTINGS[chat_id] = not current_status
        
        new_state_str = "מופעלת" if GROUP_SETTINGS[chat_id] else "מנוטרלת"
        await query.answer(f"הקבוצה כעת {new_state_str}!")
        
        # מעדכן את התפריט בלייב
        await show_groups_settings_menu(query.message, is_edit=True)

# חיפוש חופשי
@Client.on_message(filters.text & ~filters.command(["start", "settings", "index", "newindex", "broadcast", "broadcast_groups", "stats", "restart", "clean", "channels", "watch", "font", "share", "tts", "paste"]))
async def search_handler(client, message):
    query = message.text
    if query.startswith("/"): return
    if len(query) < 2: return

    status_msg = await message.reply("🔍 **מחפש עבורך בקבוצות, רגע אחד...**", quote=True)

    live_results = await search_in_telegram_groups(query)
    
    results = []
    if live_results:
        for item in live_results:
            results.append({
                'file_name': f"[{item['chat_title']}] {item['file_name']}",
                'msg_link': item['msg_link']
            })

    try: 
        await status_msg.delete()
    except Exception: 
        pass

    if not results:
        try:
            msg = await message.reply(f"**לא נמצאו תוצאות לחיפוש: `{query}`** 🙅‍♂️", quote=True)
            await asyncio.sleep(3)
            await msg.delete()
        except Exception: 
            pass
        return

    try:
        await send_results_page(client, message, results, 1, query)
    except Exception as e:
        print(f"Error sending results: {e}")

async def send_results_page(client, message, results, page, query, is_edit=False):
    per_page = 10
    total_results = len(results)
    total_pages = (total_results + per_page - 1) // per_page
    
    start_idx = (page - 1) * per_page
    current_batch = results[start_idx : start_idx + per_page]
    
    text = f"<b>🔍 <i><u>תוצאות חיפוש</u></i></b>\n\n"
    text += f"<blockquote><b>📌 חיפשת:</b> <code>{query}</code></blockquote>\n"
    text += f"<blockquote><b>🖥 נמצאו:</b> <code>{total_results} תוצאות</code></blockquote>\n\n"
    
    keyboard = []
    for res in current_batch:
        clean = clean_filename(res['file_name'])
        keyboard.append([InlineKeyboardButton(clean, url=res['msg_link'])])

    nav = []
    if page > 1: nav.append(InlineKeyboardButton('⬅️ דף קודם', callback_data=f"search#{query}#{page-1}"))
    if page < total_pages: nav.append(InlineKeyboardButton('דף הבא ➡️', callback_data=f"search#{query}#{page+1}"))
    if nav: keyboard.append(nav)
    
    keyboard.append([InlineKeyboardButton(f"📃 עמוד {page} מתוך {total_pages}", callback_data="noop")])

    markup = InlineKeyboardMarkup(keyboard)
    
    if is_edit:
        await message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    else:
        await message.reply_text(text, reply_markup=markup, disable_web_page_preview=True, quote=True)