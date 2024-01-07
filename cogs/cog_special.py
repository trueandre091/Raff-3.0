import datetime

import disnake
from disnake.ext import commands
import time

from DB.DataBase import UserDBase
from cogs.guilds_functions import guild_sets_check

DB = UserDBase()


async def create_message(
    member: disnake.Member, timedelta: datetime.timedelta, channel: disnake.TextChannel
):
    embed_dict = {
        "title": "Выдача очков участникам последнего ивента",
        "description": f"{member.mention} - {timedelta}\n",
        "footer": {"text": member.guild.name},
        "color": 0x2B2D31,
    }
    try:
        embed_dict["footer"]["icon_url"] = member.guild.icon.url
    except AttributeError:
        embed_dict["footer"][
            "icon_url"
        ] = "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png"

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
            while_event = False
            for event in member.guild.scheduled_events:
                if "active" in str(event.status):
                    while_event = True

            if after.channel.id in settings["CHANNELS"] and while_event:
                t1 = time.time()
                OnSpecialEvents.list_of_members[str(member.id)] = t1

        elif (
            before.channel
            and after.channel is None
            and str(member.id) in OnSpecialEvents.list_of_members
        ):
            if before.channel.id in settings["CHANNELS"]:
                t2 = time.time()
                need_time = settings["TIME"]
                delta = t2 - OnSpecialEvents.list_of_members[str(member.id)]

                if delta >= need_time:
                    await create_message(
                        member, delta, member.guild.get_channel(settings["LOGS_CHANNEL"])
                    )

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

                member_str = (
                    interaction.message.embeds[-1].to_dict()["description"].split()[0]
                )
                member_id = int(member_str.strip("<@>"))
                member = interaction.guild.get_member(member_id)

                default_scores = 1
                if settings["ROLES"]:
                    for roles_set in settings["ROLES"]:
                        if roles_set["ROLES_ID"] == "everyone":
                            default_scores = roles_set["SCORES"]
                            continue

                        roles_need = []
                        for role_id in roles_set["ROLES_ID"]:
                            roles_need.append(interaction.guild.get_role(role_id))

                        if any(map(lambda v: v in roles_need, member.roles)):
                            user = await DB.add_user(
                                {
                                    "ds_id": member.id,
                                    "username": member.name,
                                    "scores": roles_set["SCORES"],
                                }
                            )
                            if user:
                                await DB.update_user(
                                    {
                                        "ds_id": user.ds_id,
                                        "username": user.username,
                                        "scores": user.scores + roles_set["SCORES"],
                                    }
                                )

                            await interaction.response.send_message(
                                f"{roles_set['SCORES']} оч. выдано {member.mention}",
                                ephemeral=True,
                            )
                            await interaction.message.edit(
                                components=disnake.ui.Button(
                                    label="Выдано",
                                    style=disnake.ButtonStyle.green,
                                    custom_id="pass",
                                )
                            )

                            return

                user = await DB.add_user(
                    {
                        "ds_id": member.id,
                        "username": member.name,
                        "scores": default_scores,
                    }
                )
                if user:
                    await DB.update_user(
                        {
                            "ds_id": user.ds_id,
                            "username": user.username,
                            "scores": user.scores + default_scores,
                        }
                    )

                await interaction.response.send_message(
                    f"{default_scores} оч. выдано {member.mention}", ephemeral=True
                )
                await interaction.message.edit(
                    components=disnake.ui.Button(
                        label="Выдано",
                        style=disnake.ButtonStyle.green,
                        custom_id="pass",
                    )
                )


def setup(bot: commands.Bot):
    bot.add_cog(OnSpecialEvents(bot))
