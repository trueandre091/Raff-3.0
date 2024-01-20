import disnake
from disnake.ext import commands
from datetime import datetime

from DB.DataBaseOld import UserDBase
from cogs.cog_guilds_functions import guild_sets_check

DB = UserDBase()


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
