from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMIN_ID
from database import get_all_groups, toggle_group_status, set_start_photo
from userbot_service import index_groups_background
import asyncio

# בדיקת הרשאת מנהל בלבד
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

@Client.on_message(filters.command("admin") & filters.private)
async def admin_panel(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 סריקת קבוצות מחדש", callback_data="admin_rescan")],
        [InlineKeyboardButton("📂 ניהול קבוצות פעילות", callback_data="admin_groups")],
        [InlineKeyboardButton("🖼️ עדכון תמונת ברוכים הבאים", callback_data="admin_change_photo")]
    ])
    await message.reply_text("⚙️ **פאנל ניהול מנהל ראשי**\nבחר אפשרות מהתפריט:", reply_markup=buttons)

@Client.on_callback_query(filters.regex("^admin_"))
async def admin_callbacks(client: Client, callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("❌ אין לך הרשאה!", show_alert=True)

    data = callback.data

    if data == "admin_rescan":
        await callback.answer("🔄 מתחיל סריקה ברקע...")
        await callback.message.edit_text("🔄 **סריקת הקבוצות והערוצים החלה ברקע...**\nתוכל להמשיך להשתמש בבוט כרגיל.")
        asyncio.create_task(index_groups_background())

    elif data == "admin_groups":
        groups = await get_all_groups()
        if not groups:
            return await callback.message.edit_text("❌ לא נמצאו קבוצות במסד הנתונים. הרץ סריקה ראשונית.")

        keyboard = []
        for g in groups:
            status_icon = "✅" if g.get("enabled", True) else "❌"
            btn_text = f"{status_icon} {g.get('title', 'קבוצה')}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_grp_{g['chat_id']}")])

        keyboard.append([InlineKeyboardButton("🔙 חזרה לפאנל", callback_data="admin_main")])
        await callback.message.edit_text("📂 **ניהול קבוצות פעילות:**\nלחץ על קבוצה כדי להפעיל או לבטל את הצגת התוצאות ממנה:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("toggle_grp_"):
        chat_id = int(data.split("_")[2])
        new_status = await toggle_group_status(chat_id)
        status_str = "מופעלת ✅" if new_status else "מועברת למצב מבוטל ❌"
        await callback.answer(f"סטטוס קבוצה עודכן: {status_str}")
        # רענון רשימת הקבוצות
        await admin_callbacks(client, CallbackQuery(id=callback.id, from_user=callback.from_user, message=callback.message, data="admin_groups"))

    elif data == "admin_change_photo":
        await callback.message.edit_text("🖼️ **שינוי תמונת ברוכים הבאים:**\nשלח כעת תמונה לצ'אט הזה והיא תוגדר אוטומטית כתמונת הפתיחה של הבוט!")

    elif data == "admin_main":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 סריקת קבוצות מחדש", callback_data="admin_rescan")],
            [InlineKeyboardButton("📂 ניהול קבוצות פעילות", callback_data="admin_groups")],
            [InlineKeyboardButton("🖼️ עדכון תמונת ברוכים הבאים", callback_data="admin_change_photo")]
        ])
        await callback.message.edit_text("⚙️ **פאנל ניהול מנהל ראשי**\nבחר אפשרות מהתפריט:", reply_markup=buttons)

# הטיפול בקבלת תמונה חדשה מהמנהל
@Client.on_message(filters.photo & filters.private)
async def set_photo_handler(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        return

    photo_id = message.photo.file_id
    await set_start_photo(photo_id)
    await message.reply_text("✅ **תמונת הברכה עודכנה בהצלחה!**\nכל משתמש שירשום `/start` יראה עכשיו את התמונה החדשה.")