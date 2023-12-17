import disnake
from disnake.ext import commands

import config as cfg


class OnSpecialEvents(commands.Cog):
    """On special events"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["SPECIAL"]

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        for settings in self.settings.values():
            roles_have = []
            for role_id in settings["ROLES_HAVE"]:
                roles_have.append(guild.get_role(role_id))

            if any(map(lambda v: v in after.roles, roles_have)):
                for role_id in settings["ROLES_GET"]:
                    await after.add_roles(guild.get_role(role_id), reason="Бустер")
            else:
                for role_id in settings["ROLES_GET"]:
                    await after.remove_roles(guild.get_role(role_id))


def setup(bot: commands.Bot):
    bot.add_cog(OnSpecialEvents(bot))
