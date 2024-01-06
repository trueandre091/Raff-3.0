import datetime as dt
from os import getcwd
import disnake
from disnake.ext import commands, tasks

from cogs.guilds_functions import guild_sets_check

FOLDER = getcwd()


async def creating_message_with_nearest_events(
    event: disnake.GuildScheduledEvent, categories: list
) -> str:
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
            unused = set(event.guild.scheduled_events) - set(used)
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
    async for msg in channel.history(limit=50):
        if "БЛИЖАЙШИЕ ИВЕНТЫ" in msg.content:
            await msg.delete()
            break


class AutoSendingMessage(commands.Cog):
    """Auto sending the message of list of events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_scheduled_event_create(self, event):
        settings = await guild_sets_check(
            event.guild.id, "GENERAL_SETTINGS", "NEAREST_EVENTS"
        )
        if settings is None:
            return

        channel = self.bot.get_channel(
            settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CHANNEL"]
        )

        await delete_previous_message(channel)
        await channel.send(
            await creating_message_with_nearest_events(
                event, settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CATEGORIES"]
            )
        )

    @commands.Cog.listener()
    async def on_guild_scheduled_event_delete(self, event):
        settings = await guild_sets_check(
            event.guild.id, "GENERAL_SETTINGS", "NEAREST_EVENTS"
        )
        if settings is None:
            return

        channel = self.bot.get_channel(
            settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CHANNEL"]
        )

        await delete_previous_message(channel)
        await channel.send(
            await creating_message_with_nearest_events(
                event, settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CATEGORIES"]
            )
        )

    @commands.Cog.listener()
    async def on_guild_scheduled_event_update(self, before, after):
        settings = await guild_sets_check(
            after.guild.id, "GENERAL_SETTINGS", "NEAREST_EVENTS"
        )
        if settings is None:
            return

        channel = self.bot.get_channel(
            settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CHANNEL"]
        )

        await delete_previous_message(channel)
        await channel.send(
            await creating_message_with_nearest_events(
                after, settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CATEGORIES"]
            )
        )


def get_next_event(startdate: dt.datetime, weekday, time):
    """
    @startdate: given date, in format '2013-05-25'
    @weekday: week day as an integer, between 0 (Monday) to 6 (Sunday)
    """
    today = startdate
    day = today + dt.timedelta((weekday - today.weekday()) % 7)
    date = day.date()
    time = dt.time(hour=19, minute=0, second=0)
    return dt.datetime.combine(date, time)


class SettingEvents(commands.Cog):
    """Auto setting weekly events (just for Homey Temple)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.events_setting.start()

    @tasks.loop(hours=12)
    async def events_setting(self):
        today = dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))
        if int(today.weekday()) == 0 and 0 <= int(today.strftime("%H")) <= 12:
            guild = self.bot.get_guild(785312593614209055)
            scheduled_events = [
                {
                    "name": "Еженедельный ивент 📩 (Сб)",
                    "channel": self.bot.get_channel(858737175439736873),
                    "scheduled_start_time": get_next_event(today, 5, 19),
                    "description": "Еженедельный ивент на сервере! Приглашаем всех желающих весело провести время с участниками сервера ❤\nJackbox Party: Смертельная вечеринка, НашШпионаж, Смехлыст и др., Мафия, Salo.fun и многое другое по решению участников ивента! Всех ждём! 🤗",
                },
                {
                    "name": "Еженедельный ивент 📩 (Вс)",
                    "channel": self.bot.get_channel(858737175439736873),
                    "scheduled_start_time": get_next_event(today, 6, 19),
                    "description": "Еженедельный ивент на сервере! Приглашаем всех желающих весело провести время с участниками сервера ❤\nJackbox Party: Смертельная вечеринка, НашШпионаж, Смехлыст и др., Мафия, Salo.fun и многое другое по решению участников ивента! Всех ждём! 🤗",
                },
            ]
            for event in scheduled_events:
                await guild.create_scheduled_event(
                    name=event["name"],
                    channel=event["channel"],
                    scheduled_start_time=event["scheduled_start_time"],
                    description=event["description"],
                )

    @events_setting.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(AutoSendingMessage(bot))
    bot.add_cog(SettingEvents(bot))
