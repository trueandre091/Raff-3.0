import disnake
from disnake.ext import commands
import time

import config as cfg
from DB.DataBase import UserDBase

DB = UserDBase()


class OnSpecialEvents(commands.Cog):
    """On special events"""

    list_of_members = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["SPECIAL"]

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        guild = self.bot.get_guild(cfg.GUILD_ID)
        for settings in self.settings["ROLES"].values():
            roles_have = []
            for role_id in settings["ROLES_HAVE"]:
                roles_have.append(guild.get_role(role_id))

            if any(map(lambda v: v in after.roles, roles_have)):
                for role_id in settings["ROLES_GET"]:
                    await after.add_roles(guild.get_role(role_id))
            else:
                for role_id in settings["ROLES_GET"]:
                    await after.remove_roles(guild.get_role(role_id))

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        if member.bot:
            return

        settings = self.settings["EVENTS"]
        if before.channel is None and after.channel.id:
            if after.channel.id in settings["CHANNELS"]:
                t1 = time.time()
                OnSpecialEvents.list_of_members[str(member.id)] = t1
        elif before.channel and after.channel is None:
            if before.channel.id in settings["CHANNELS"]:
                t2 = time.time()
                need_time = settings["TIME"]
                delta = t2 - OnSpecialEvents.list_of_members[str(member.id)]
                print(need_time, delta, member.name)

                if delta >= need_time:
                    user = await DB.get_user({"ds_id": member.id})
                    if user is None:
                        await DB.add_user(
                            {
                                "ds_id": member.id,
                                "username": member.name,
                                "scores": settings["SCORES"],
                            }
                        )
                    else:
                        await DB.update_user(
                            {
                                "ds_id": user.ds_id,
                                "username": user.username,
                                "scores": user.scores + settings["SCORES"],
                            }
                        )


def setup(bot: commands.Bot):
    bot.add_cog(OnSpecialEvents(bot))
