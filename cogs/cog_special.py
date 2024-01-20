import disnake
from disnake.ext import commands
from datetime import datetime
import math

from DB.DataBaseOld import UserDBase
from DB.models import Users
from cogs.cog_guilds_functions import guild_sets_check, GDB

DB = UserDBase()


async def convert_ex_to_lvl(user: Users, factor: int = 5):
    if user is None:
        return 0

    lvl = math.floor(math.pow(user.experience / factor, 1 / 3))

    return lvl


async def check_for_role(user, settings):
    role = None
    for role_set in settings["REWARDS"]:
        if role_set["ROLE"] and role_set["AMOUNT"]:
            if user.scores >= role_set["AMOUNT"]:
                try:
                    if user.scores > role["AMOUNT"]:
                        role = role_set
                except TypeError:
                    role = role_set
    return role


async def top_create_embed(bot: commands.Bot, settings: dict, embed_dict: dict):
    """Creating an embed of leaderboard of members by scores"""
    guild = bot.get_guild(settings["GUILD_ID"])
    settings = settings["COGS"]["SCORES"]

    top = await GDB.get_top_users_by_scores(guild.id)
    if top is None:
        top = []

    roles = {}
    place = 0
    for user in top:
        member = guild.get_member(user.ds_id)
        if member is None or user.scores == 0:
            continue

        embed_dict[
            "description"
        ] += f"`{place + 1}.` {member.mention} — `{user.scores} оч.`\n"

        role_set = await check_for_role(user, settings)
        if role_set:
            if roles[str(role_set["ROLE"])]:
                roles[str(role_set["ROLE"])].append(user.ds_id)
            else:
                roles[str(role_set["ROLE"])] = [user.ds_id]
        place += 1

    if roles:
        embed_dict["description"] += "\n**Получат роли**"
        for role, users in roles.items():
            embed_dict["fields"].append(
                {"name": f"{guild.get_role(role).name}:", "value": "", "inline": True}
            )
            for user in users:
                member = guild.get_member(user.ds_id)
                embed_dict["fields"][-1]["value"] += f"{member.mention} "

    return embed_dict


class OnSpecialEvents(commands.Cog):
    """On special events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        settings = await guild_sets_check(after.guild.id, "GENERAL", "ROLES")
        if settings is None:
            return

        guild = self.bot.get_guild(settings["GUILD_ID"])
        settings = settings["COGS"]["SPECIAL"]["ROLES"]

        for settings in settings.values():
            roles_have = []
            for role_id in settings["ROLES_HAVE"]:
                role = guild.get_role(role_id)
                if role is None:
                    continue
                roles_have.append(role)

            if any(map(lambda v: v in after.roles, roles_have)):
                for role_id in settings["ROLES_GET"]:
                    role = guild.get_role(role_id)
                    if role is None:
                        continue
                    await after.add_roles(role)
            else:
                for role_id in settings["ROLES_GET"]:
                    role = guild.get_role(role_id)
                    if role is None:
                        continue
                    await after.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        """Greeting newbies when they come"""
        settings = await guild_sets_check(member.guild.id, "GENERAL", "WELCOME")
        if settings is None:
            return

        settings = settings["COGS"]["WELCOME"]

        channel = self.bot.get_channel(settings["CHANNEL"])
        variables = {
            "member.mention": member.mention,
            "member.name": member.name,
            "member.nick": member.nick,
            "member": member,
        }
        embed_dict = {
            "title": settings["EMBED"]["TITLE"].format(**variables),
            "description": settings["EMBED"]["DESCRIPTION"].format(**variables),
            "image": {"url": settings["EMBED"]["IMAGE"]},
            "thumbnail": {},
            "color": settings["EMBED"]["COLOR"],
            "timestamp": str(datetime.now()),
        }
        try:
            embed_dict["thumbnail"]["url"] = member.avatar.url
        except AttributeError:
            embed_dict["thumbnail"]["url"] = settings["AVATAR_IF_ERROR"]

        await channel.send(embed=disnake.Embed.from_dict(embed_dict))

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        """Farewell to members when they leave"""
        settings = await guild_sets_check(member.guild.id, "GENERAL", "FAREWELL")
        if settings is None:
            return
        settings = settings["COGS"]["FAREWELL"]

        channel = self.bot.get_channel(settings["CHANNEL"])
        variables = {
            "member.mention": member.mention,
            "member.name": member.name,
            "member.nick": member.nick,
            "member": member,
        }

        await channel.send(settings["MESSAGE"].format(**variables))


def setup(bot: commands.Bot):
    bot.add_cog(OnSpecialEvents(bot))
