import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import UPDATE_CHANNEL, REQUEST_GROUP, PHOTO_URL, ADMINS
from Tj_Bots.search import APPROVED_USERS, REQUIRE_APPROVAL
from database import get_start_photo, set_start_photo, get_all_groups, toggle_group_status
from userbot_service import index_groups_background

def check_is_admin(user_id):
    if isinstance(ADMINS, list):
        return any(str(user_id) == str(admin) for admin in ADMINS)
    return str(user_id) == str(ADMINS)

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        user = message.from_user
        
        if check_is_admin(user.id):
            APPROVED_USERS.add(user.id)
            return await send_home_message(client, message)

        import Tj_Bots.search as search_mod
        if search_mod.REQUIRE_APPROVAL and user.id not in APPROVED_USERS:
            await message.reply("⏳ **בקשת הגישה שלך נשלחה למנהל.**\nתקבל הודעה ברגע שהגישה תאושר!", quote=True)
            
            admin_btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ אישור משתמש", callback_data=f"approve_user_{user.id}"),
                 InlineKeyboardButton("❌ דחייה", callback_data=f"deny_user_{user.id}")]
            ])
            admin_list = ADMINS if isinstance(ADMINS, list) else [ADMINS]
            for admin_id in admin_list:
                try:
                    await client.send_message(
                        admin_id,
                        f"🔔 **בקשת גישה חדשה לבוט!**\n\n• **משתמש:** {user.mention}\n• **ID:** `{user.id}`",
                        reply_markup=admin_btn
                    )
                except Exception:
                    pass
            return

        await send_home_message(client, message)

async def send_home_message(client, message, user=None, is_edit=False):
    if not user:
        user = message.from_user
    
    user_mention = user.mention
    bot_name = client.me.first_name
    bot_username = client.me.username
    bot_mention = f"[{bot_name}](https://t.me/{bot_username})"
    
    current_photo = await get_start_photo() or PHOTO_URL
    
    buttons = [
        [InlineKeyboardButton("🔍 חיפוש סרט", callback_data="btn_search")],
        [InlineKeyboardButton('✇ קבוצת בקשות ✇', url=REQUEST_GROUP), InlineKeyboardButton('✇ ערוץ עדכונים ✇', url=f'https://t.me/{UPDATE_CHANNEL}')],
        [InlineKeyboardButton('⇋ להוספה לקבוצה ⇋', url=f"http://t.me/{client.me.username}?startgroup&admin=delete_messages")]
    ]
    
    if check_is_admin(user.id):
        buttons.append([InlineKeyboardButton("⚙️ פאנל מנהל", callback_data="admin_panel")])
        buttons.append([InlineKeyboardButton("🧹 מחיקת כל ההתכתבות", callback_data="clear_chat_action")])

    txt = (f"**היי {user_mention} 👋**\n"
           f"**ברוכים הבאים ל- {bot_mention}** 😎\n\n"
           "**אני מנוע חיפוש סרטים וסדרות חדשני,**\n"
           "<b>התפקיד שלי זה לחפש סרטים בקבוצות,\n"
           "הוסיפו אותי לקבוצה שלכם ואני אמשיך מכאן.</b> ☄️\n\n"
           f"<blockquote>**👨🏼‍💻 מתכנת ראשי: @danielhaliva**</blockquote>")
    
    if is_edit:
        await message.edit_media(InputMediaPhoto(current_photo, caption=txt), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_photo(current_photo, caption=txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

async def show_admin_panel(message, is_edit=False):
    import Tj_Bots.search as search_mod
    approval_status = "🔒 פעיל (נדרש אישור)" if search_mod.REQUIRE_APPROVAL else "🔓 מבוטל (חופשי לכולם)"
    
    txt = (f"<b>👑 פאנל ניהול ראשי</b>\n\n"
           f"• **מנגנון אישור משתמשים:** {approval_status}\n"
           f"• **משתמשים מאושרים:** `{len(APPROVED_USERS)}`\n\n"
           "בחר פעולה מהכפתורים למטה:")
    
    toggle_btn_txt = "🔓 בטל חסימת משתמשים" if search_mod.REQUIRE_APPROVAL else "🔒 הפעל חסימת משתמשים"
    
    buttons = [
        [InlineKeyboardButton(toggle_btn_txt, callback_data="toggle_approval")],
        [InlineKeyboardButton("👥 ניהול וביטול משתמשים", callback_data="admin_users")],
        [InlineKeyboardButton("🔄 סריקת קבוצות מחדש", callback_data="admin_rescan")],
        [InlineKeyboardButton("📂 ניהול קבוצות פעילות", callback_data="admin_groups")],
        [InlineKeyboardButton("🖼️ עדכון תמונת ברוכים הבאים", callback_data="admin_change_photo")],
        [InlineKeyboardButton("🧹 מחק את כל ההתכתבות", callback_data="clear_chat_action")],
        [InlineKeyboardButton("🏠 חזרה לבית", callback_data="home")]
    ]
    if is_edit:
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

@Client.on_message(filters.photo & filters.private)
async def set_photo_handler(client, message):
    if check_is_admin(message.from_user.id):
        photo_id = message.photo.file_id
        await set_start_photo(photo_id)
        await message.reply_text("✅ **תמונת הברכה עודכנה בהצלחה!**\nכל משתמש שירשום `/start` יראה כעת את התמונה החדשה.", quote=True)

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    # מענה מיידי לטלגרם למניעת טעינה אינסופית
    try:
        await query.answer()
    except Exception:
        pass

    import Tj_Bots.search as search_mod
    data = query.data
    user_id = query.from_user.id
    is_admin_user = check_is_admin(user_id)

    if data == "btn_search":
        return await query.message.reply_text("פשוט רשום לי את שם הסרט או הסדרה שאתה מחפש! 🔎", quote=True)

    elif data == "admin_panel" and is_admin_user:
        await show_admin_panel(query.message, is_edit=True)

    elif data == "admin_users" and is_admin_user:
        if not APPROVED_USERS:
            return await query.message.edit_text("❌ אין כרגע משתמשים מאושרים במערכת.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 חזרה לפאנל", callback_data="admin_panel")]]))
        
        keyboard = []
        for uid in list(APPROVED_USERS):
            keyboard.append([InlineKeyboardButton(f"🚫 בטל אישור ל- ID: {uid}", callback_data=f"revoke_user_{uid}")])
        keyboard.append([InlineKeyboardButton("🔙 חזרה לפאנל מנהל", callback_data="admin_panel")])
        
        await query.message.edit_text(f"👥 **משתמשים מאושרים ({len(APPROVED_USERS)}):**\nלחץ על משתמש לבטול אישור:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("revoke_user_") and is_admin_user:
        target_uid = int(data.split("revoke_user_")[1])
        if target_uid in APPROVED_USERS:
            APPROVED_USERS.remove(target_uid)
            try:
                await client.send_message(target_uid, "🚫 **גישתך לבוט בוטלה על ידי המנהל.**")
            except Exception:
                pass
        
        keyboard = []
        for uid in list(APPROVED_USERS):
            keyboard.append([InlineKeyboardButton(f"🚫 בטל אישור ל- ID: {uid}", callback_data=f"revoke_user_{uid}")])
        keyboard.append([InlineKeyboardButton("🔙 חזרה לפאנל מנהל", callback_data="admin_panel")])
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_rescan" and is_admin_user:
        await query.message.edit_text("🔄 **סריקת הקבוצות והערוצים החלה ברקע...**\nתוכל להמשיך להשתמש בבוט כרגיל.")
        asyncio.create_task(index_groups_background())

    elif data == "admin_groups" and is_admin_user:
        groups = await get_all_groups()
        if not groups:
            return await query.message.edit_text("❌ לא נמצאו קבוצות במסד הנתונים. הרץ סריקה ראשונית.")

        keyboard = []
        for g in groups:
            status_icon = "✅" if g.get("enabled", True) else "❌"
            btn_text = f"{status_icon} {g.get('title', 'קבוצה')}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_grp_{g['chat_id']}")])

        keyboard.append([InlineKeyboardButton("🔙 חזרה לפאנל מנהל", callback_data="admin_panel")])
        await query.message.edit_text("📂 **ניהול קבוצות פעילות:**\nלחץ על קבוצה כדי להפעיל או לבטל את הצגת התוצאות ממנה:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("toggle_grp_") and is_admin_user:
        chat_id = int(data.split("toggle_grp_")[1])
        await toggle_group_status(chat_id)
        
        groups = await get_all_groups()
        keyboard = []
        for g in groups:
            status_icon = "✅" if g.get("enabled", True) else "❌"
            btn_text = f"{status_icon} {g.get('title', 'קבוצה')}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_grp_{g['chat_id']}")])
        keyboard.append([InlineKeyboardButton("🔙 חזרה לפאנל מנהל", callback_data="admin_panel")])
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_change_photo" and is_admin_user:
        await query.message.edit_text("🖼️ **שינוי תמונת ברוכים הבאים:**\nשלח כעת תמונה בצ'אט הזה והיא תוגדר אוטומטית כתמונת הפתיחה של הבוט!")

    elif data.startswith("approve_user_") and is_admin_user:
        target_id = int(data.split("approve_user_")[1])
        APPROVED_USERS.add(target_id)
        await query.message.edit_text(f"{query.message.text}\n\n✅ **אושר על ידי המנהל!**")
        try:
            await client.send_message(target_id, "🎉 **גישתך לבוט אושרה!** כעת תוכל לשלוח שמות של סרטים לחיפוש.")
        except Exception:
            pass

    elif data.startswith("deny_user_") and is_admin_user:
        await query.message.edit_text(f"{query.message.text}\n\n❌ **נדחה על ידי המנהל.**")

    elif data == "toggle_approval" and is_admin_user:
        search_mod.REQUIRE_APPROVAL = not search_mod.REQUIRE_APPROVAL
        await show_admin_panel(query.message, is_edit=True)

    elif data == "clear_chat_action":
        try:
            msg_ids = list(range(max(1, query.message.id - 100), query.message.id + 1))
            await client.delete_messages(chat_id=query.message.chat.id, message_ids=msg_ids)
        except Exception:
            pass

    elif data == "home":
        await send_home_message(client, query.message, user=query.from_user, is_edit=True)
