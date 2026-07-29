import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import UPDATE_CHANNEL, REQUEST_GROUP, PHOTO_URL, ADMINS, LOG_CHANNEL, AUTH_CHANNEL_FORCE
from database import db
from .utils import get_readable_size

async def send_file_with_fallback(client, chat_id, file_data, reply_to_id=None):
    try:
        await client.copy_message(
            chat_id=chat_id,
            from_chat_id=file_data['chat_id'],
            message_id=file_data['message_id'],
            caption=None,
            reply_to_message_id=reply_to_id
        )
        return True
    except Exception:
        file_id = file_data.get('file_id')
        if not file_id:
            return False
            
        file_name = file_data.get('file_name', '')
        file_size = get_readable_size(file_data.get('file_size', 0))
        fallback_caption = f"**{file_name}**\n\n**💾 גודל: {file_size}**"
        
        try:
            await client.send_video(
                chat_id=chat_id,
                video=file_id,
                caption=fallback_caption,
                reply_to_message_id=reply_to_id
            )
            return True
        except Exception:
            try:
                await client.send_document(
                    chat_id=chat_id,
                    document=file_id,
                    caption=fallback_caption,
                    reply_to_message_id=reply_to_id
                )
                return True
            except Exception:
                return False

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.from_user.id
        
        if len(message.command) > 1:
            file_db_id = message.command[1]
            
            should_check = AUTH_CHANNEL_FORCE
            is_subbed = True
            
            if should_check:
                try:
                    await client.get_chat_member(UPDATE_CHANNEL, user_id)
                except Exception:
                    is_subbed = False

            if not is_subbed:
                btn = [[InlineKeyboardButton('📣 להרשמה לערוץ', url=f'https://t.me/{UPDATE_CHANNEL}')],
                       [InlineKeyboardButton('↻ נסה שוב', callback_data=f"checksub_{file_db_id}")]]
                
                return await message.reply_text(
                    "**כדי להשתמש בבוט הזה עליך להיות מנוי לערוץ העדכונים שלו!🫰**",
                    reply_markup=InlineKeyboardMarkup(btn),
                    quote=True
                )

            file_data = await db.get_file(file_db_id)
            if file_data:
                success = await send_file_with_fallback(client, message.chat.id, file_data, message.id)
                if not success:
                    await message.reply("❌ הקובץ נמחק מהמקור או שאין לי גישה אליו.", quote=True)
            return

        bot_name = client.me.first_name
        bot_username = client.me.username
        bot_mention = f"[{bot_name}](https://t.me/{bot_username})"

        anim_msg = await message.reply_text(
             f"<blockquote>**__היי <tg-emoji emoji-id='5195448447062251797'>👋</tg-emoji>__**\n**__ברוכים הבאים ל- {bot_mention} <tg-emoji emoji-id='5325559344513691205'>😎</tg-emoji>__**</blockquote>", 
             quote=True
        )        
        await asyncio.sleep(0.5)
        
        await send_home_message(client, message)
        await anim_msg.delete()

    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply("היי! אני מוכן לחיפוש סרטים 🎬", quote=True)

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
        [InlineKeyboardButton('✇ קבוצת בקשות ✇', url=REQUEST_GROUP), 
         InlineKeyboardButton('✇ ערוץ עדכונים ✇', url=f'https://t.me/{UPDATE_CHANNEL}')],
        [InlineKeyboardButton('⇋ להוספה לקבוצה ⇋', url=f"http://t.me/{client.me.username}?startgroup&admin=delete_messages")]
    ]
    
    txt = (f"**היי {user_mention} <tg-emoji emoji-id='5195448447062251797'>👋</tg-emoji>**\n"
            f"**ברוכים הבאים ל- {bot_mention}** <tg-emoji emoji-id='5325559344513691205'>😎</tg-emoji>\n\n"
           "**אני מנוע חיפוש סרטים וסדרות חדשני,**"
           "\n<b>התפקיד שלי זה לחפש סרטים בקבוצות,"
           "\nהוסיפו אותי לקבוצה שלכם ואני אמשיך מכאן.</b><tg-emoji emoji-id='5224607267797606837'>☄️</tg-emoji>\n\n"
           "<blockquote>**👨🏼‍💻 מתכנת ראשי: @BOSS1480**</blockquote>")
    
    if is_edit:
        await message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_photo(PHOTO_URL, caption=txt, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

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

    elif data == "home":
        await send_home_message(client, query.message, user=query.from_user, is_edit=True)
    
    elif data == "help":
        user_mention = query.from_user.mention
        
        btns = [
            [InlineKeyboardButton('הגדרות קבוצה', callback_data='help_settings'), InlineKeyboardButton('זכויות יוצרים', callback_data='help_copyright')],
            [InlineKeyboardButton('תוספות (Extra)', callback_data='help_extra'), InlineKeyboardButton('מדריך שימוש', callback_data='help_guide')],
            [InlineKeyboardButton('🏠 בית 🏠', callback_data='home')]
        ]
        
        await query.message.edit_media(
            InputMediaPhoto(PHOTO_URL, caption=f"<b>היי {user_mention},\nכאן תוכל לקבל עזרה עבור כל הפקודות שלי.</b>"), 
            reply_markup=InlineKeyboardMarkup(btns)
        )

    elif data == "help_extra":
        txt = "<b><u>פקודות נוספות:</u></b>\n\n• <code>/id</code> - מזהה משתמש\n• <code>/info</code> - פרטי משתמש"
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help')]]))

    elif data == "help_guide":
        txt = "<b>💡 מדריך לחיפוש סרטים:</b>\n\nכדי לבקש סרט או סדרה, פשוט רשום את השם המדויק בצ'אט (לדוגמה: <code>פאודה</code>)."
        btn = [[InlineKeyboardButton('למעבר לקבוצה 💬', url=REQUEST_GROUP)], [InlineKeyboardButton('חזרה ⋟', callback_data='help')]]
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup(btn))

    elif data == "help_copyright":
        txt = "<b>© זכויות יוצרים</b>\n\nהקבצים בבוט נאספים מטלגרם באופן אוטומטי."
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help')]]))
    
    elif data == "help_settings":
        txt = "<b>⚙️ הגדרות קבוצה</b>\n\nשלחו <code>/settings</code> בקבוצה כדי להתאימה."
        await query.message.edit_media(InputMediaPhoto(PHOTO_URL, caption=txt), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('חזרה ⋟', callback_data='help')]]))

    elif data == "closea":
        try:
            await query.message.delete()
        except Exception:
            pass