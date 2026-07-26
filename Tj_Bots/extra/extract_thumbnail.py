import os
from pyrogram import Client, filters

@Client.on_message(filters.command("extract_thumbnail"))
async def extract_thumbnail_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ הגב על וידאו או קובץ עם תמונה ממוזערת.", quote=True)
    
    reply = message.reply_to_message
    media = reply.video or reply.document or reply.animation or reply.audio
    
    if not media or not hasattr(media, "thumbs") or not media.thumbs:
        return await message.reply_text("❌ לא נמצאה תמונה ממוזערת (Thumbnail) במדיה הזו.", quote=True)

    status = await message.reply_text("⏳ **מחלץ תמונה ממוזערת...**", quote=True)
    
    try:
      
        thumb = media.thumbs[-1]
        file_path = await client.download_media(thumb.file_id)
        
        if file_path:
            await message.reply_photo(
                photo=file_path,
                quote=True
            )
            await status.delete()
            
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            await status.edit("❌ נכשלה הורדת התמונה הממוזערת.")
            
    except Exception as e:
        await status.edit(f"❌ שגיאה בחילוץ: `{e}`")
