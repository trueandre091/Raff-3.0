from os import getcwd
import disnake
from disnake.ext import commands, tasks
from datetime import datetime, timezone, timedelta

from cogs.cog_guilds_functions import GDB, DB, find_guilds_by_param, guild_sets_check
from cogs.cog_scores import top_create_embed

FOLDER = getcwd()


class AutoUpdateMessagesTop(commands.Cog):
    """Send/edit an autoupdate message about leaderboard of weekly amount of members' messages"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aup_top.start()
        self.reset_aup_top.start()

    @tasks.loop(hours=12)
    async def reset_aup_top(self):
        """Resetting the database of members' weekly amount of messages"""
        today = datetime.now(timezone(timedelta(hours=3)))
        if int(today.weekday()) == 0 and 0 <= int(today.strftime("%H")) <= 12:
            guilds = await find_guilds_by_param(
                self.bot,
                "GENERAL_SETTINGS",
                "AUTOUPDATE_MESSAGES",
                "MESSAGES",
                encode=False,
            )

            for guild in guilds:
                top = await GDB.get_top_users_by_messages(guild.guild_id)
                if top:
                    settings = await guild_sets_check(guild.guild_id)
                    settings["COGS_SETTINGS"]["COUNTERS"]["MESSAGES_PREVIOUS_BESTS"] = [
                        user.ds_id for user in top[0:3]
                    ]
                    print(
                        settings["COGS_SETTINGS"]["COUNTERS"]["MESSAGES_PREVIOUS_BESTS"]
                    )

                    await GDB.update_guild(
                        {"guild_id": guild.guild_id, "guild_sets": settings}
                    )

                users = guild.users
                for user in users:
                    await DB.update_user({"ds_id": user.ds_id, "messages": 0})

    @reset_aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=45)
    async def aup_top(self):
        guilds = await find_guilds_by_param(
            self.bot, "GENERAL_SETTINGS", "AUTOUPDATE_MESSAGES", "MESSAGES"
        )

        for settings in guilds:
            channel = self.bot.get_channel(
                settings["COGS_SETTINGS"]["AUTOUPDATE"]["CHANNEL"]
            )
            guild = self.bot.get_guild(settings["GUILD_ID"])
            if channel is None:
                continue

            top = await GDB.get_top_users_by_messages(guild.id)
            if top is None:
                continue

            embed_dict = {
                "title": "Таблица лидеров по сообщениям за неделю: 📊",
                "description": "",
                "fields": [],
                "color": 0x2B2D31,
                "footer": {"text": guild.name},
            }
            try:
                embed_dict["footer"]["icon_url"] = guild.icon.url
            except AttributeError:
                embed_dict["footer"][
                    "icon_url"
                ] = "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png"

            place = 1
            for user in top:
                if (
                    place
                    <= settings["COGS_SETTINGS"]["AUTOUPDATE"]["MESSAGES"]["PLACE_LIMIT"]
                ):
                    member = guild.get_member(user.ds_id)
                    if member is None or user.messages == 0:
                        continue
                    embed_dict[
                        "description"
                    ] += f"`{place}.` {member.mention} - {user.messages}\n"
                    place += 1

            flag = True
            async for msg in channel.history(limit=50):
                try:
                    if (
                        "Таблица лидеров по сообщениям за неделю"
                        in msg.embeds[-1].to_dict()["title"]
                    ):
                        await msg.edit(embed=disnake.Embed.from_dict(embed_dict))
                        flag = False
                        break
                except:
                    pass
            if flag:
                await channel.send(embed=disnake.Embed.from_dict(embed_dict))

    @aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


class AutoUpdateScoresTop(commands.Cog):
    """Send/edit an autoupdate message about leaderboard of amount of members' scores"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aup_top.start()

    @tasks.loop(minutes=1)
    async def aup_top(self):
        guilds = await find_guilds_by_param(
            self.bot, "GENERAL_SETTINGS", "AUTOUPDATE_MESSAGES", "SCORES"
        )

        for settings in guilds:
            channel = self.bot.get_channel(
                settings["COGS_SETTINGS"]["AUTOUPDATE"]["CHANNEL"]
            )
            if channel is None:
                continue

            embed_dict = {
                "title": "Таблица лидеров по очкам за месяц: 📊",
                "description": "",
                "fields": [],
                "color": 0x2B2D31,
                "footer": {},
            }
            try:
                embed_dict["footer"]["icon_url"] = channel.guild.icon.url
            except AttributeError:
                embed_dict["footer"][
                    "icon_url"
                ] = "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png"

            embed_dict = await top_create_embed(self.bot, settings, embed_dict)

            flag = True
            async for msg in channel.history(limit=50):
                try:
                    if (
                        "Таблица лидеров по очкам за месяц"
                        in msg.embeds[0].to_dict()["title"]
                    ):
                        await msg.edit(embed=disnake.Embed.from_dict(embed_dict))
                        flag = False
                        break
                except:
                    pass
            if flag:
                await channel.send(embed=disnake.Embed.from_dict(embed_dict))

    @aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(AutoUpdateScoresTop(bot))
    bot.add_cog(AutoUpdateMessagesTop(bot))
