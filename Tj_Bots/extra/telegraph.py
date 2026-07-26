import os
import asyncio
import base64
import requests
from pyrogram import Client, filters

IBB_API_KEY = "1df1187bacd48b090e524c2f1bae6945"

def upload_to_ibb(file_path):
    url = "https://api.imgbb.com/1/upload"
    try:
        with open(file_path, "rb") as file:
            # Base64 encoding is safer for some APIs
            img_base64 = base64.b64encode(file.read()).decode('utf-8')
            payload = {
                "key": IBB_API_KEY,
                "image": img_base64,
            }
            res = requests.post(url, data=payload)
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                return data["data"]["url"]
            else:
                error_msg = data.get("error", {}).get("message", "Unknown IBB error")
                return f"ERROR: {error_msg}"
    except Exception as e:
        return f"EXCEPTION: {str(e)}"

@Client.on_message(filters.command("telegraph"))
async def telegraph_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ הגב על תמונה להעלאה ל-IBB.", quote=True)
    
    reply = message.reply_to_message
    
    if reply.photo:
        status = await message.reply_text("⏳ **מעלה תמונה ל-IBB...**", quote=True)
        file_path = await reply.download()
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, upload_to_ibb, file_path)
            
            if result.startswith("http"):
                await status.edit(f"✅ **התמונה הועלתה בהצלחה:**\n{result}", disable_web_page_preview=False)
            else:
                await status.edit(f"❌ שגיאה: `{result}`")
        except Exception as e:
            await status.edit(f"❌ שגיאה: `{e}`")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await message.reply_text("❌ ניתן להעלות רק תמונות דרך פקודה זו.", quote=True)
