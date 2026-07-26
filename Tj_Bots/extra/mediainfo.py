import os
import asyncio
import secrets
import aiofiles
from pyrogram import Client, filters
from telegraph.aio import Telegraph

section_dict = {"General": "🗒", "Video": "🎞", "Audio": "🔊", "Text": "🔠", "Menu": "🗃"}

def parseinfo(out, size):
    tc = ""
    trigger = False
    size_line = f"File size                                 : {size / (1024 * 1024):.2f} MiB"
    if size > 1024 * 1024 * 1024:
        size_line = f"File size                                 : {size / (1024 * 1024 * 1024):.2f} GiB"

    for line in out.split("\n"):
        line = line.strip()
        if not line: continue

        found_section = False
        for section, emoji in section_dict.items():
            if line.startswith(section) and ":" not in line:
                trigger = True
                if not line.startswith("General"):
                    tc += "</pre><br>"
                tc += f"<h4>{emoji} {line.replace('Text', 'Subtitle')}</h4>"
                found_section = True
                break
        
        if found_section:
            continue

        if line.startswith("File size"):
            line = size_line
        
        if trigger:
            tc += "<br><pre>"
            trigger = False
        
        tc += line + "\n"
    
    tc += "</pre><br>"
    return tc

async def create_telegraph_page(title, content, client):
    telegraph = Telegraph()
    
    me = await client.get_me()
    author_name = me.first_name
    author_url = f"https://t.me/{me.username}"

    await telegraph.create_account(
        short_name=secrets.token_hex(4),
        author_name=author_name,
        author_url=author_url
    )
    
    response = await telegraph.create_page(
        title=title,
        html_content=content,
        author_name=author_name,
        author_url=author_url
    )
    return response['url']

@Client.on_message(filters.command("mediainfo"))
async def mediainfo_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ הגב על קובץ מדיה.", quote=True)
    
    media = message.reply_to_message
    file_obj = media.video or media.document or media.audio
    
    if not file_obj:
        return await message.reply_text("❌ אין מדיה מתאימה בהודעה.", quote=True)

    status = await message.reply_text("⏳ **מעבד נתונים...**", quote=True)
    
    file_path = f"mi_{media.id}_{secrets.token_hex(2)}.dat"
    
    try:
        chunk_size = 0
        limit = 20 * 1024 * 1024 
        
        async with aiofiles.open(file_path, "wb") as f:
            async for chunk in client.stream_media(file_obj):
                await f.write(chunk)
                chunk_size += len(chunk)
                if chunk_size > limit:
                    break

        proc = await asyncio.create_subprocess_shell(
            f'mediainfo "{file_path}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode().strip()

        if not output:
            return await status.edit("❌ שגיאה בהפקת המידע (mediainfo לא מותקן או נכשל).")

        file_name = getattr(file_obj, "file_name", "Unknown File")
        
        parsed_content = parseinfo(output, file_obj.file_size)
        final_html = f"<h4>📌 {file_name}</h4><br><br>{parsed_content}"
        
        link = await create_telegraph_page("MediaInfo Result", final_html, client)
        
        await status.edit(
            f"**MediaInfo:\n\n➲ Link :** {link}",
            disable_web_page_preview=False
        )

    except Exception as e:
        await status.edit(f"❌ שגיאה: `{e}`")
        
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
