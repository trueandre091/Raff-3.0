import datetime

import disnake
from disnake.ext import commands
import time

from DB.DataBase import UserDBase
from cogs.cog_guilds_functions import guild_sets_check

DB = UserDBase()


class OnSpecialEvents(commands.Cog):
    """On special events"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        settings = await guild_sets_check(
            after.guild.id, "GENERAL_SETTINGS", "AUTO_ADDING_ROLES"
        )
        if settings is None:
            return
        guild = self.bot.get_guild(settings["GUILD_ID"])
        settings = settings["COGS_SETTINGS"]["SPECIAL"]["ROLES"]

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


def setup(bot: commands.Bot):
    bot.add_cog(OnSpecialEvents(bot))
