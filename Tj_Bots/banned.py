from pyrogram import Client

@Client.on_message(group=-10)
async def ban_enforcer(client, message):
    pass