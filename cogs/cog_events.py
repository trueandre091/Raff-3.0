from os import getcwd
import disnake
from disnake.ext import commands
import asyncio

from cogs.guilds_functions import guild_sets_check, DB, GDB, encoder

FOLDER = getcwd()


async def creating_message_with_nearest_events(event: disnake.GuildScheduledEvent, categories: list) -> str:
    """Creating an embed"""
    dict_of_categories = {}
    used = []
    categories.append("Другие")
    for category in categories:
        dict_of_categories[category] = []
        if category != "Другие":
            for event in event.guild.scheduled_events:
                if category in event.name or category in event.description:
                    dict_of_categories[category].append(event)
                    used.append(event)
        else:
            unused = event.guild.scheduled_events - used
            for event in unused:
                dict_of_categories[category].append(event)

    message = "# БЛИЖАЙШИЕ ИВЕНТЫ\n"
    for category, events in dict_of_categories.items():
        if events:
            message += f"* {category}:\n"
            for event in events:
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

    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event):
        guild = await guild_sets_check(event.guild.id, "GENERAL_SETTINGS", "NEAREST_EVENTS")
        if not guild:
            return

        guild = await GDB.get_guild({"guild_id": event.guild.id})
        settings = encoder.code_from_json(guild.guild_sets)["COGS_SETTINGS"]["EVENTS"]
        channel = self.bot.get_channel(settings["CHANNEL"])

        await delete_previous_message(channel)
        await channel.send(await creating_message_with_nearest_events(event, settings["CATEGORIES"]))

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
        guild = await guild_sets_check(event.guild.id, "GENERAL_SETTINGS", "NEAREST_EVENTS")
        if not guild:
            return

        guild = await GDB.get_guild({"guild_id": event.guild.id})
        settings = encoder.code_from_json(guild.guild_sets)["COGS_SETTINGS"]["EVENTS"]
        channel = self.bot.get_channel(settings["CHANNEL"])

        await delete_previous_message(channel)
        await channel.send(await creating_message_with_nearest_events(event, settings["CATEGORIES"]))

    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(self, before, after):
        guild = await guild_sets_check(after.guild.id, "GENERAL_SETTINGS", "NEAREST_EVENTS")
        if not guild:
            return

        guild = await GDB.get_guild({"guild_id": after.guild.id})
        settings = encoder.code_from_json(guild.guild_sets)["COGS_SETTINGS"]["EVENTS"]
        channel = self.bot.get_channel(settings["CHANNEL"])

        await delete_previous_message(channel)
        await channel.send(await creating_message_with_nearest_events(after, settings["CATEGORIES"]))


def setup(bot: commands.Bot):
    bot.add_cog(AutoSendingMessage(bot))
