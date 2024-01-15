import datetime as dt
from os import getcwd
import disnake
from disnake.ext import commands, tasks

from cogs.cog_guilds_functions import guild_sets_check, DB

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
    async def on_guild_scheduled_event_update(
        self, before: disnake.GuildScheduledEvent, after: disnake.GuildScheduledEvent
    ):
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
            names = ["Еженедельный ивент 📩 (Сб)", "Еженедельный ивент 📩 (Вс)"]
            for event in guild.scheduled_events:
                if event.name in names:
                    return

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


async def create_message(member: disnake.Member, timedelta, channel: disnake.TextChannel):
    embed_dict = {
        "title": "Выдача очков участникам последнего ивента",
        "fields": [{"name": f"{timedelta}", "value": f"{member.mention}"}],
        "footer": {"text": member.guild.name},
        "color": 0x2B2D31,
    }
    try:
        embed_dict["footer"]["icon_url"] = member.guild.icon.url
    except AttributeError:
        embed_dict["footer"][
            "icon_url"
        ] = "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png"

    flag = True
    async for msg in channel.history(limit=1):
        try:
            if (
                "Выдача очков участникам последнего ивента"
                in msg.embeds[-1].to_dict()["title"]
            ):
                flag = False
                embed = msg.embeds[-1].to_dict()
                embed["fields"].append(
                    {"name": f"{timedelta}", "value": f"{member.mention}"}
                )
                await msg.edit(
                    embed=disnake.Embed.from_dict(embed),
                    components=[
                        disnake.ui.Button(
                            label="Выдать очки",
                            style=disnake.ButtonStyle.grey,
                            custom_id="accept_member",
                        ),
                        disnake.ui.Button(
                            label="Отклонить",
                            style=disnake.ButtonStyle.red,
                            custom_id="deny",
                        ),
                    ],
                )
        except:
            pass

    if flag:
        await channel.send(
            embed=disnake.Embed.from_dict(embed_dict),
            components=[
                disnake.ui.Button(
                    label="Выдать очки",
                    style=disnake.ButtonStyle.grey,
                    custom_id="accept_member",
                ),
                disnake.ui.Button(
                    label="Отклонить",
                    style=disnake.ButtonStyle.red,
                    custom_id="deny",
                ),
            ],
        )


class UserOnEvent:
    list_of_members = []

    def __init__(
        self,
        guild: disnake.Guild,
        ds_id: int,
        channel: id = None,
        settings: list = None,
    ):
        self.guild = guild
        self.ds_id = ds_id
        self.channel = channel
        self.minutes = -1
        self.minutes_out = -1
        self.settings = settings
        self.check_for_event.start()

    @tasks.loop(minutes=1)
    async def check_for_event(self):
        event_check = None
        for event in self.guild.scheduled_events:
            if "active" in str(event.status):
                event_check = event.id
                self.channel = event.channel.id
                break

        if event_check is None:
            if self.minutes >= self.settings["TIME"]:
                member = self.guild.get_member(self.ds_id)
                logs_channel = self.guild.get_channel(self.settings["LOGS_CHANNEL"])

                await create_message(member, self.minutes, logs_channel)

                UserOnEvent.list_of_members.remove(self)
                self.check_for_event.stop()
            else:
                self.minutes_out += 1
                if self.minutes_out >= 60:
                    UserOnEvent.list_of_members.remove(self)
                    self.check_for_event.stop()

        member = self.guild.get_member(self.ds_id)
        if member.voice is None:
            return

        if member.voice.channel.id == self.channel and event_check:
            self.minutes += 1
            print(self.ds_id, self.minutes)


class AutoScoresAdding(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        settings = await guild_sets_check(
            member.guild.id,
            "GENERAL_SETTINGS",
            "AUTO_ADDING_SCORES_FOR_TIME_IN_VOICE_CHANNEL",
        )
        if not settings:
            return
        settings = settings["COGS_SETTINGS"]["SPECIAL"]["EVENTS"]
        channels = settings["CHANNELS"]

        if before.channel != after.channel:
            if after.channel is None:
                return

            if after.channel.id in channels:
                flag = True
                for user in UserOnEvent.list_of_members:
                    if user.ds_id == member.id:
                        flag = False

                if flag:
                    user_obj = UserOnEvent(
                        member.guild,
                        member.id,
                        None,
                        settings,
                    )
                    UserOnEvent.list_of_members.append(user_obj)
                    print(user_obj.ds_id)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.type == disnake.InteractionType.component:
            if interaction.component.custom_id == "accept_member":
                settings = await guild_sets_check(
                    interaction.guild.id,
                    "GENERAL_SETTINGS",
                    "AUTO_ADDING_SCORES_FOR_TIME_IN_VOICE_CHANNEL",
                )
                if settings is None:
                    await interaction.response.send_message(
                        "Данная функция отключена на сервере", ephemeral=True
                    )
                    return

                member = interaction.guild.get_member(interaction.author.id)
                if not member.guild_permissions.administrator:
                    await interaction.response.send_message(
                        "Эта команда вам недоступна", ephemeral=True
                    )
                    return

                settings = settings["COGS_SETTINGS"]["SPECIAL"]["EVENTS"]

                fields = interaction.message.embeds[-1].to_dict()["fields"]
                for field in fields:
                    member_str = field["value"]
                    member_id = int(member_str.strip("<@>"))
                    member = interaction.guild.get_member(member_id)

                    scores = 1
                    if settings["ROLES"]:
                        for roles_set in settings["ROLES"]:
                            if roles_set["ROLES_ID"] == "everyone":
                                scores = roles_set["SCORES"]
                                continue

                            roles_need = []
                            for role_id in roles_set["ROLES_ID"]:
                                roles_need.append(interaction.guild.get_role(role_id))

                            if any(map(lambda v: v in roles_need, member.roles)):
                                scores = roles_set["SCORES"]

                        user = await DB.add_user(
                            {
                                "ds_id": member.id,
                                "username": member.name,
                                "scores": scores,
                            }
                        )
                        if user:
                            await DB.update_user(
                                {
                                    "ds_id": user.ds_id,
                                    "username": user.username,
                                    "scores": user.scores + scores,
                                }
                            )

                await interaction.response.send_message(f"Очки выданы", ephemeral=True)
                await interaction.message.edit(
                    components=disnake.ui.Button(
                        label="Выдано",
                        style=disnake.ButtonStyle.green,
                        custom_id="pass",
                    )
                )


def setup(bot: commands.Bot):
    bot.add_cog(AutoSendingMessage(bot))
    bot.add_cog(SettingEvents(bot))
    bot.add_cog(AutoScoresAdding(bot))
