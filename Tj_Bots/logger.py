from pyrogram import Client

@Client.on_message(group=-1)
async def global_logger(client, message):
    pass