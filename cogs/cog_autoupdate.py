"""Автообновление всех топов на сервере"""

from os import getcwd
import disnake
from disnake.ext import commands, tasks
from json import load, dump
from datetime import datetime, timezone, timedelta

FOLDER = getcwd()
with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


class AutoUpdateMessagesTop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aup_top.start()
        self.reset_aup_top.start()
        self.channel = CONFIG["CHANNEL_AUP_TOP"]

    @tasks.loop(hours=12)
    async def reset_aup_top(self):
        today = datetime.now(timezone(timedelta(hours=3)))
        if int(today.weekday()) == 0 and int(today.strftime('%H')) >= 0:
            with (open(f"{FOLDER}/data/lb_messages_data.json", "r", encoding="utf-8") as f):
                data = load(f)

            data.clear()

            with (open(f"{FOLDER}/data/lb_messages_data.json", "w", encoding="utf-8") as f):
                dump(data, f)

    @reset_aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=15)
    async def aup_top(self):
        channel = self.bot.get_channel(self.channel)
        guild = self.bot.get_guild(CONFIG["GUILD_ID"])

        with (open(f"{FOLDER}/data/lb_messages_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        data = dict(sort_data)

        none_members = []
        for key in data:
            if guild.get_member(int(key)) not in guild.members:
                none_members.append(key)
        for key in none_members:
            data.pop(key)

        embed_dict = {
            'title': 'Таблица лидеров по сообщениям за неделю: 📊',
            'description': '',
            'fields': [],
            'color': 0x2b2d31,
            'footer': {'text': channel.guild.name, 'icon_url': channel.guild.icon.url}
        }

        place = 1
        for key, value in data.items():
            if place <= 10:
                member = guild.get_member(int(key))
                embed_dict['description'] += f"`{place}.` {member.mention} - {value}\n"
                place += 1

        flag = True
        async for msg in channel.history(limit=3):
            if 'Таблица лидеров по сообщениям за неделю' in msg.embeds[0].to_dict()['title']:
                await msg.edit(embed=disnake.Embed.from_dict(embed_dict))
                flag = False
                break

        if flag:
            await channel.send(embed=disnake.Embed.from_dict(embed_dict))

    @aup_top.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


class AutoUpdateScoresTop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aup_top.start()
        self.channel = CONFIG["CHANNEL_AUP_TOP"]

    @tasks.loop(seconds=60)
    async def aup_top(self):
        channel = self.bot.get_channel(self.channel)
        guild = self.bot.get_guild(CONFIG["GUILD_ID"])

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        data = dict(sort_data)

        nulls = []
        for key, value in data.items():
            if value == 0:
                nulls.append(key)
        for key in nulls:
            data.pop(key)

        first_lvl_members = []
        third_lvl_members = []
        fifth_lvl_members = []
        amount1 = CONFIG["SETTINGS"]["AMOUNT_TO_FIRST_LVL"]
        amount2 = CONFIG["SETTINGS"]["AMOUNT_TO_THIRD_LVL"]
        amount3 = CONFIG["SETTINGS"]["AMOUNT_TO_FIFTH_LVL"]

        embed_dict = {
            'title': 'Таблица лидеров по очкам: 📊',
            'description': '',
            'fields': [],
            'color': 0x2b2d31,
            'footer': {'text': channel.guild.name, 'icon_url': channel.guild.icon.url}
        }

        flag1 = False
        flag2 = False
        flag3 = False
        c = 1
        for key, value in data.items():
            member = guild.get_member(int(key))
            embed_dict['description'] += f"`{c}.` {member.mention} — `{value} оч.`\n"
            if amount1 <= value < amount2:
                flag1 = True
                first_lvl_members.append(key)
            elif amount2 <= value < amount3:
                flag2 = True
                third_lvl_members.append(key)
            elif amount3 <= value:
                flag3 = True
                fifth_lvl_members.append(key)
            c += 1

        c = 0
        if flag1 or flag2 or flag3:
            embed_dict['description'] += "\n**Получат роли**"

        if flag1:
            embed_dict['fields'].append({'name': '1-го уровня:', 'value': '', 'inline': True})
            for key in first_lvl_members:
                member = guild.get_member(int(key))
                embed_dict['fields'][c]['value'] += f"{member.mention} "
            c += 1
        if flag2:
            embed_dict['fields'].append({'name': '3-го уровня:', 'value': '', 'inline': True})
            for key in third_lvl_members:
                member = guild.get_member(int(key))
                embed_dict['fields'][c]['value'] += f"{member.mention} "
            c += 1

        if flag3:
            embed_dict['fields'].append({'name': '5-го уровня:', 'value': '', 'inline': True})
            for key in fifth_lvl_members:
                member = guild.get_member(int(key))
                embed_dict['fields'][c]['value'] += f"{member.mention} "
            c += 1

        flag = True
        async for msg in channel.history(limit=3):
            if 'Таблица лидеров по очкам' in msg.embeds[0].to_dict()['title']:
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
