from os import getcwd
import disnake
from disnake.ext import commands, tasks
from json import load, dump
from datetime import datetime, timezone, timedelta

from cogs.guilds_functions import guild_sets_check, GDB, DB
import config as cfg
from cogs.cog_scores import top_create_embed

FOLDER = getcwd()


class AutoUpdateMessagesTop(commands.Cog):
    """Send/edit an autoupdate message about leaderboard of weekly amount of members' messages"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["AUTOUPDATE"]
        self.aup_top.start()
        self.reset_aup_top.start()

    @tasks.loop(hours=12)
    async def reset_aup_top(self):
        """Resetting the database of members' weekly amount of messages"""
        today = datetime.now(timezone(timedelta(hours=3)))
        if int(today.weekday()) == 0 and 0 <= int(today.strftime("%H")) <= 12:
            with open(f"{FOLDER}/data/lb_messages_data.json", "r", encoding="utf-8") as f:
                data = load(f)

            guild = self.bot.get_guild(cfg.GUILD_ID)
            sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
            data = dict(sort_data)

            limit = 1
            for key in data:
                member = guild.get_member(int(key))
                if member is None or limit == self.settings["PREVIOUS_BESTS_LIMIT"]:
                    data.pop(key)
                    continue
                with open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f:
                    counters = load(f)

                counters["PREVIOUS_BESTS"].append(key)

                with open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f:
                    dump(counters, f)
                limit += 1

            with open(f"{FOLDER}/data/lb_messages_data.json", "w", encoding="utf-8") as f:
                dump({}, f)

    @reset_aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=15)
    async def aup_top(self):
        channel = self.bot.get_channel(self.settings["CHANNEL"])
        guild = self.bot.get_guild(cfg.GUILD_ID)

        with open(f"{FOLDER}/data/lb_messages_data.json", "r", encoding="utf-8") as f:
            data = load(f)
        with open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f:
            counters = load(f)

        sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        data = dict(sort_data)

        embed_dict = {
            "title": "Таблица лидеров по сообщениям за неделю: 📊",
            "description": "",
            "fields": [],
            "color": 0x2B2D31,
            "footer": {"text": guild.name, "icon_url": guild.icon.url},
        }

        place = 1
        for key, value in data.items():
            if place <= self.settings["MESSAGES"]["PLACE_LIMIT"]:
                member = guild.get_member(int(key))
                if member is None:
                    data.pop(key)
                    continue
                embed_dict["description"] += f"`{place}.` {member.mention} - {value}\n"
                place += 1

        if len(counters["PREVIOUS_BESTS"]):
            embed_dict["fields"].append({"name": "Топ 3 предыдущей недели:", "value": ""})
            for key in counters["PREVIOUS_BESTS"]:
                embed_dict["fields"][-1]["value"] += f"{guild.get_member(int(key)).mention} "

        flag = True
        async for msg in channel.history(limit=3):
            if "Таблица лидеров по сообщениям за неделю" in msg.embeds[0].to_dict()["title"]:
                await msg.edit(embed=disnake.Embed.from_dict(embed_dict))
                flag = False
                break
        if flag:
            await channel.send(embed=disnake.Embed.from_dict(embed_dict))

    @aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


class AutoUpdateScoresTop(commands.Cog):
    """Send/edit an autoupdate message about leaderboard of amount of members' scores"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["AUTOUPDATE"]
        self.aup_top.start()

    @tasks.loop(seconds=60)
    async def aup_top(self):
        channel = self.bot.get_channel(self.settings["CHANNEL"])

        embed_dict = {
            "title": "Таблица лидеров по очкам: 📊",
            "description": "",
            "fields": [],
            "color": 0x2B2D31,
            "footer": {"text": channel.guild.name, "icon_url": channel.guild.icon.url},
        }
        embed_dict = await top_create_embed(self.bot, embed_dict)

        flag = True
        async for msg in channel.history(limit=3):
            if "Таблица лидеров по очкам" in msg.embeds[0].to_dict()["title"]:
                await msg.edit(embed=disnake.Embed.from_dict(embed_dict))
                flag = False
                break
        if flag:
            await channel.send(embed=disnake.Embed.from_dict(embed_dict))

    @aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(AutoUpdateScoresTop(bot))
    bot.add_cog(AutoUpdateMessagesTop(bot))
