import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import UPDATE_CHANNEL, REQUEST_GROUP, PHOTO_URL, ADMINS
from userbot_service import get_all_user_chats, GROUP_SETTINGS

ADMIN_CODE = "1234"
CODE_REQUIRED = True
AUTHENTICATED_USERS = set()

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
    
    if user.id in ADMINS:
        buttons.append([InlineKeyboardButton("⚙️ פאנל מנהל", callback_data="admin_panel")])
        buttons.append([InlineKeyboardButton("🧹 מחיקת כל ההתכתבות", callback_data="clear_chat_action")])

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

@Client.on_message(filters.command("auth") & filters.private)
async def auth_command(client, message):
    global AUTHENTICATED_USERS
    if len(message.command) > 1:
        code_input = message.command[1].strip()
        if code_input == ADMIN_CODE:
            AUTHENTICATED_USERS.add(message.from_user.id)
            await message.reply("✅ הקוד נכון! הוענקה לך גישה מלאה לפאנל המנהל.", quote=True)
        else:
            await message.reply("❌ קוד גישה שגוי!", quote=True)
    else:
        await message.reply("🔑 נא לשלוח את הקוד בצורה: `/auth 1234`", quote=True)

async def show_admin_panel(message, is_edit=False):
    code_status = "🔒 פעיל" if CODE_REQUIRED else "🔓 מבוטל"
    txt = (f"<b>👑 פאנל ניהול ראשי</b>\n\n"
           f"• **סטטוס קוד גישה:** {code_status}\n"
           f"• **קוד נוכחי:** `{ADMIN_CODE}`\n\n"
           "בחר פעולה מהכפתורים למטה:")
    
    toggle_btn_txt = "🔓 בטל דרישת קוד" if CODE_REQUIRED else "🔒 הפעל דרישת קוד"
    
    buttons = [
        [InlineKeyboardButton("👥 ניהול קבוצות חיפוש", callback_data="manage_groups")],
        [InlineKeyboardButton(toggle_btn_txt, callback_data="toggle_code")],
        [InlineKeyboardButton("🧹 מחק את כל ההתכתבות", callback_data="clear_chat_action")],
        [InlineKeyboardButton("🏠 חזרה לבית", callback_data="home")]
    ]
    if is_edit:
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

async def show_groups_manager(message):
    chats = await get_all_user_chats()
    if not chats:
        return await message.edit_text("❌ לא נמצאו קבוצות פעילות בחשבון ה-Userbot.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("חזרה ⋟", callback_data="admin_panel")]]))

    buttons = []
    for chat in chats:
        is_active = GROUP_SETTINGS.get(chat.id, True)
        status_icon = "✅" if is_active else "❌"
        buttons.append([InlineKeyboardButton(f"{status_icon} {chat.title}", callback_data=f"toggle_grp_{chat.id}")])

    buttons.append([InlineKeyboardButton("🏠 חזרה לפאנל", callback_data="admin_panel")])
    
    txt = "<b>👥 ניהול קבוצות לחיפוש סרטים:</b>\nלחץ על קבוצה כדי להפעיל (✅) או לבטל (❌) את החיפוש בה."
    await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    global CODE_REQUIRED
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

    elif data == "admin_panel":
        if user_id not in ADMINS:
            return await query.answer("❌ אין לך הרשאות מנהל!", show_alert=True)
            
        if CODE_REQUIRED and user_id not in AUTHENTICATED_USERS:
            await query.answer("🔒 נדרש קוד גישה!", show_alert=True)
            return await query.message.reply_text("🔒 **הגישה לפאנל מנהל מוגנת בקוד!**\nשלח בצ'אט את הפקודה:\n`/auth 1234`", quote=True)
            
        await show_admin_panel(query.message, is_edit=True)

    elif data == "manage_groups" and user_id in ADMINS:
        await query.answer("טוען קבוצות...")
        await show_groups_manager(query.message)

    elif data.startswith("toggle_grp_") and user_id in ADMINS:
        group_id = int(data.split("toggle_grp_")[1])
        current_val = GROUP_SETTINGS.get(group_id, True)
        GROUP_SETTINGS[group_id] = not current_val
        await query.answer(f"סטטוס הקבוצה שונה!", show_alert=False)
        await show_groups_manager(query.message)

    elif data == "toggle_code" and user_id in ADMINS:
        CODE_REQUIRED = not CODE_REQUIRED
        status_txt = "בוטלה" if not CODE_REQUIRED else "הופעלה"
        await query.answer(f"דרישת קוד הגישה {status_txt}!", show_alert=True)
        await show_admin_panel(query.message, is_edit=True)

    elif data == "clear_chat_action":
        await query.answer("מנקה את ההתכתבות...")
        try:
            msg_ids = list(range(max(1, query.message.id - 100), query.message.id + 1))
            await client.delete_messages(chat_id=query.message.chat.id, message_ids=msg_ids)
        except Exception:
            pass

    elif data == "home":
        await send_home_message(client, query.message, user=query.from_user, is_edit=True)

    elif data == "help":
        btns = [[InlineKeyboardButton('🏠 בית 🏠', callback_data='home')]]
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption="<b>מדריך עזרה לבוט חיפוש סרטים.</b>"), reply_markup=InlineKeyboardMarkup(btns))