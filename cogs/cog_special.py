import disnake
from disnake.ext import commands
import time

from DB.DataBase import UserDBase
from cogs.guilds_functions import guild_sets_check

DB = UserDBase()


class OnSpecialEvents(commands.Cog):
    """On special events"""

    list_of_members = {}

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
