import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import UPDATE_CHANNEL, REQUEST_GROUP, PHOTO_URL, ADMINS
from Tj_Bots.search import APPROVED_USERS, REQUIRE_APPROVAL

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        user = message.from_user
        
        # מנהל נכנס ישר ללא דרישת אישור
        if user.id in ADMINS:
            APPROVED_USERS.add(user.id)
            return await send_home_message(client, message)

        # בדיקה אם מנגנון האישורים פעיל
        import Tj_Bots.search as search_mod
        if search_mod.REQUIRE_APPROVAL and user.id not in APPROVED_USERS:
            await message.reply("⏳ **בקשת הגישה שלך נשלחה למנהל.**\nתקבל הודעה ברגע שהגישה תאושר!", quote=True)
            
            # שליחת הודעה למנהלים לאישור
            admin_btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ אישור משתמש", callback_data=f"approve_user_{user.id}"),
                 InlineKeyboardButton("❌ דחייה", callback_data=f"deny_user_{user.id}")]
            ])
            for admin_id in ADMINS:
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
           f"<blockquote>**👨🏼‍💻 מתכנת ראשי: @danielhaliva**</blockquote>")
    
    if is_edit:
        await message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_photo(PHOTO_URL, caption=txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

async def show_admin_panel(message, is_edit=False):
    import Tj_Bots.search as search_mod
    approval_status = "🔒 פעיל (נדרש אישור)" if search_mod.REQUIRE_APPROVAL else "🔓 מבוטל (חופשי לכולם)"
    
    txt = (f"<b>👑 פאנל ניהול ראשי</b>\n\n"
           f"• **מנגנון אישור משתמשים:** {approval_status}\n"
           f"• **משתמשים מאושרים:** {len(APPROVED_USERS)}\n\n"
           "בחר פעולה מהכפתורים למטה:")
    
    toggle_btn_txt = "🔓 בטל חסימת משתמשים" if search_mod.REQUIRE_APPROVAL else "🔒 הפעל חסימת משתמשים"
    
    buttons = [
        [InlineKeyboardButton(toggle_btn_txt, callback_data="toggle_approval")],
        [InlineKeyboardButton("🧹 מחק את כל ההתכתבות", callback_data="clear_chat_action")],
        [InlineKeyboardButton("🏠 חזרה לבית", callback_data="home")]
    ]
    if is_edit:
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    import Tj_Bots.search as search_mod
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

    elif data.startswith("approve_user_") and user_id in ADMINS:
        target_id = int(data.split("approve_user_")[1])
        APPROVED_USERS.add(target_id)
        await query.answer("✅ המשתמש אושר בהצלחה!", show_alert=True)
        await query.message.edit_text(f"{query.message.text}\n\n✅ **אושר על ידי המנהל!**")
        try:
            await client.send_message(target_id, "🎉 **גישתך לבוט אושרה!** כעת תוכל לשלוח שמות של סרטים לחיפוש.")
        except Exception:
            pass

    elif data.startswith("deny_user_") and user_id in ADMINS:
        await query.answer("❌ הבקשה נדחתה.", show_alert=True)
        await query.message.edit_text(f"{query.message.text}\n\n❌ **נדחה על ידי המנהל.**")

    elif data == "toggle_approval" and user_id in ADMINS:
        search_mod.REQUIRE_APPROVAL = not search_mod.REQUIRE_APPROVAL
        status_txt = "הופעלה" if search_mod.REQUIRE_APPROVAL else "בוטלה"
        await query.answer(f"חסימת משתמשים {status_txt}!", show_alert=True)
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