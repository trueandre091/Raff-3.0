import disnake
from disnake.ext import commands
from random import randint
import math

from cogs.cog_guilds_functions import guild_sets_check, DB, is_none
from DB.models import Users


async def convert_ex_to_lvl(user: Users, factor: int = 5):
    if user is None:
        return 0

    lvl = math.floor(math.pow(user.experience / factor, 1 / 3))

    return lvl


async def count_experience(message: disnake.Message, settings: dict):
    if not settings["GENERAL"]["EXPERIENCE"] or message.author.bot:
        return

    settings = settings["COGS"]["EXPERIENCE"]

    lvl1 = await convert_ex_to_lvl(await DB.get_user(ds_id=message.author.id))

    flag = True
    skip_first_flag = False
    async for msg in message.channel.history(limit=50):
        if (
            message.created_at.minute == msg.created_at.minute
            and msg.author == message.author
            and skip_first_flag
        ):
            flag = False
            break
        skip_first_flag = True

    if flag:
        ex = randint(5, 10)

        user = await DB.add_user(
            ds_id=message.author.id,
            username=message.author.name,
            experience=ex,
        )
        if user:
            await DB.update_user(
                ds_id=user.ds_id,
                username=user.username,
                experience=user.experience + ex,
            )

    lvl2 = await convert_ex_to_lvl(await DB.get_user(ds_id=message.author.id))

    if lvl1 != lvl2:
        await message.reply(
            f"{message.author.mention}, поздравляю с {lvl2} уровнем <a:A_applecatrun:992319318425620542>"
        )

        settings = settings["REWARDS"]
        all_roles_id = []
        role = None
        for role_set in settings:
            if role_set["ROLE"] and role_set["AMOUNT"]:
                all_roles_id.append(role_set["ROLE_ID"])
                if lvl2 >= role_set["AMOUNT"]:
                    try:
                        if lvl2 > role["AMOUNT"]:
                            role = role_set
                    except TypeError:
                        role = role_set

        await message.author.add_roles(message.guild.get_role(role["ROLE"]))

        all_roles_id.remove(role["ROLE"])
        for role_id in all_roles_id:
            await message.author.remove_roles(message.guild.get_role(role_id))


class ExperienceCommands(commands.Cog):
    """Commands to set nums of users' experience"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Прибавить опыт любому кол-ву участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def add_ex(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Adding to several members a certain amount of experience"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "EXPERIENCE")
        if await is_none(interaction, settings):
            return

        guild = interaction.guild
        members_list = участники.split()
        members_list_values = []

        for member in members_list:
            member_id = int(member.strip("<@>"))
            member = guild.get_member(member_id)
            user = await DB.add_user(
                ds_id=member_id,
                username=member.name,
                experience=количество,
            )
            if user:
                await DB.update_user(
                    ds_id=user.ds_id,
                    username=user.username,
                    experience=user.experience + количество,
                )
                members_list_values.append(user.experience + количество)
            else:
                members_list_values.append(количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} опыта было прибавлено к указанным участникам",
            description="Настоящее количество опыта у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.experience} опыта```",
            )

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(
        description="Вычесть опыт любому кол-ву участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def remove_ex(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Adding to several members a certain amount of scores"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "EXPERIENCE")
        if await is_none(interaction, settings):
            return

        members_list = участники.split()
        members_list_values = []

        for member in members_list:
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            if user is None:
                members_list_values.append(0)
            else:
                if количество >= user.experience:
                    await DB.update_user(
                        ds_id=user.ds_id,
                        username=user.username,
                        experience=0,
                    )
                    members_list_values.append(0)
                else:
                    await DB.update_user(
                        ds_id=user.ds_id,
                        username=user.username,
                        experience=user.experience - количество,
                    )
                    members_list_values.append(user.experience - количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} опыта было вычтено у указанных участников",
            description="Настоящее количество опыта у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.experience} опыта```",
            )

        await interaction.response.send_message(embed=embed)


class MessagesCommands(commands.Cog):
    """Command to set nums of users' messages"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Прибавить опыт любому кол-ву участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def set_msg(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Setting to several members a certain amount of messages"""
        settings = await guild_sets_check(
            interaction.guild.id, "GENERAL", "AUTOUPDATE", "MESSAGES"
        )
        if await is_none(interaction, settings):
            return

        guild = interaction.guild
        members_list = участники.split()
        members_list_values = []

        for member in members_list:
            member_id = int(member.strip("<@>"))
            member = guild.get_member(member_id)
            user = await DB.add_user(
                ds_id=member.id,
                username=member.name,
                messages=количество,
            )
            if user:
                await DB.update_user(
                    ds_id=user.ds_id,
                    username=user.username,
                    messages=количество,
                )
            members_list_values.append(количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} сообщений было установлено указанным участникам",
            description="Настоящее количество сообщений у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.messages} опыта```",
            )

        await interaction.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ExperienceCommands(bot))
    bot.add_cog(MessagesCommands(bot))
