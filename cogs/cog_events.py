from json import load
from os import getcwd
from disnake.ext import commands
import time

FOLDER = getcwd()
with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event):
        channel = self.bot.get_channel(CONFIG["CHANNEL_EVENTS"])
        async for message in channel.history(limit=1):
            await message.delete()

        time.sleep(2)

        weekly = []
        special = []
        flag1 = False
        flag2 = False
        for event in event.guild.scheduled_events:
            if "недель" in event.name:
                flag1 = True
                weekly.append(event)
            elif "актив" in event.name:
                flag1 = True
                weekly.append(event)
            else:
                flag2 = True
                special.append(event)
        message = "# БЛИЖАЙШИЕ ИВЕНТЫ\n"
        if flag1:
            message += "* Еженедельные ивенты:\n"
            for event in weekly:
                message += f"{event.url}\n"
        if flag2:
            message += "* Особые ивенты:\n"
            for event in special:
                message += f"{event.url}\n"

        await channel.send(message)

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
        channel = self.bot.get_channel(CONFIG["CHANNEL_EVENTS"])
        async for message in channel.history(limit=1):
            await message.delete()

        time.sleep(2)

        weekly = []
        special = []
        flag1 = False
        flag2 = False
        for event in event.guild.scheduled_events:
            if "недель" in event.name:
                flag1 = True
                weekly.append(event)
            elif "актив" in event.name:
                flag1 = True
                weekly.append(event)
            else:
                flag2 = True
                special.append(event)
        message = "# БЛИЖАЙШИЕ ИВЕНТЫ\n"
        if flag1:
            message += "* Еженедельные ивенты:\n"
            for event in weekly:
                message += f"{event.url}\n"
        if flag2:
            message += "* Особые ивенты:\n"
            for event in special:
                message += f"{event.url}\n"

        await channel.send(message)

    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(self, before, after):
        channel = self.bot.get_channel(CONFIG["CHANNEL_EVENTS"])
        async for message in channel.history(limit=1):
            await message.delete()

        time.sleep(2)

        weekly = []
        special = []
        flag1 = False
        flag2 = False
        for event in after.guild.scheduled_events:
            if str(event.status) not in ['canceled', 'completed']:
                if "недель" in event.name:
                    flag1 = True
                    weekly.append(event)
                elif "актив" in event.name:
                    flag1 = True
                    weekly.append(event)
                else:
                    flag2 = True
                    special.append(event)

        message = "# БЛИЖАЙШИЕ ИВЕНТЫ\n"
        if flag1:
            message += "* Еженедельные ивенты:\n"
            for event in weekly:
                message += f"{event.url}\n"
        if flag2:
            message += "* Особые ивенты:\n"
            for event in special:
                message += f"{event.url}\n"

        await channel.send(message)


def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))
