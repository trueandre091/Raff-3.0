import disnake
from disnake.ext import commands
from random import randint

import config as cfg
from DB.DataBase import UserDBase

DB = UserDBase()


async def count_experience(message: disnake.Message):
    minute = message.created_at.minute
    flag = True
    skip_first_flag = False
    async for msg in message.channel.history(limit=None):
        if msg.created_at.minute == minute:
            if msg.author == message.author and skip_first_flag:
                flag = False
                break

            skip_first_flag = True

    if flag:
        ex = randint(5, 10)

        user = await DB.get_user({"ds_id": message.author.id})
        if not user:
            await DB.add_user({"ds_id": message.author.id, "username": message.author.id, "experience": ex})
        else:
            await DB.update_user({"ds_id": user.disc_id, "username": user.username, "experience": user.experience + ex})

        user = await DB.get_user({'ds_id': message.author.id})
        await message.reply(f"Чек {message.author.name} !")
