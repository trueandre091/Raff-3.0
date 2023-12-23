from os import getcwd
import disnake
from disnake.ext import commands
import asyncio

import config as cfg

FOLDER = getcwd()


async def creating_message_with_nearest_events(
    event: disnake.GuildScheduledEvent,
) -> str:
    """Creating an embed"""
    weekly, special = [], []
    flag1, flag2 = False, False
    for event in event.guild.scheduled_events:
        if "недель" in event.name or "недель" in event.description:
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
    return message


async def delete_previous_message(channel) -> None:
    async for message in channel.history(limit=1):
        await message.delete()
    await asyncio.sleep(2)


class AutoSendingMessage(commands.Cog):
    """Auto sending the message of list of events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["EVENTS"]
        self.channel = self.bot.get_channel(self.settings["CHANNEL"])

    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event):
        channel = self.bot.get_channel(self.settings["CHANNEL"])

        await delete_previous_message(channel)
        await channel.send(await creating_message_with_nearest_events(event))

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
        channel = self.bot.get_channel(self.settings["CHANNEL"])

        await delete_previous_message(channel)
        await channel.send(await creating_message_with_nearest_events(event))

    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(self, before, after):
        channel = self.bot.get_channel(self.settings["CHANNEL"])

        await delete_previous_message(channel)
        await channel.send(await creating_message_with_nearest_events(after))


def setup(bot: commands.Bot):
    bot.add_cog(AutoSendingMessage(bot))
