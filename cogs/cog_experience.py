import disnake
from disnake.ext import commands
from random import randint
from datetime import timedelta

import config as cfg
from DB.DataBase import UserDBase
from DB.models import Users

DB = UserDBase()


async def count_experience(message: disnake.Message):
    if message.author.bot:
        return

    minute = timedelta(minutes=1)
    flag = True
    skip_first_flag = False
    async for msg in message.channel.history(limit=50):
        delta = message.created_at - msg.created_at
        if delta <= minute and msg.author == message.author and skip_first_flag:
            flag = False
            break
        skip_first_flag = True

    if flag:
        ex = randint(5, 10)

        user = await DB.get_user({"ds_id": message.author.id})
        if not user:
            await DB.add_user({"ds_id": message.author.id, "username": message.author.id, "experience": ex})
        else:
            await DB.update_user({"ds_id": user.ds_id, "username": user.username, "experience": user.experience + ex})


class ExperienceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # @commands.slash_command(description="Посмотреть опыт на сервере")
    # async def add_ex(self, interaction: disnake.ApplicationCommandInteraction, участник: disnake.Member = None):
    #     if
