import disnake
from disnake.ext import commands

from cogs.cog_guilds_functions import guild_sets_check, DB, is_none
from bot import set, add, remove


class ExperienceCommands(commands.Cog):
    """Commands to set nums of users' experience"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @add.sub_command(
        description="Прибавить опыт любому кол-ву участников (упомянуть через пробел)",
    )
    async def exp(
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

    @remove.sub_command(
        description="Вычесть опыт любому кол-ву участников (упомянуть через пробел)",
    )
    async def exp(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Adding to several members a certain amount of experience"""
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

    @set.sub_command(
        description="Установить опыт любому кол-ву участников (упомянуть через пробел)",
    )
    async def exp(
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
                    experience=user.experience - количество,
                )

        embed = disnake.Embed(
            title=f"{количество} опыта было вычтено у указанных участников",
            description="Настоящее количество опыта у каждого:",
            color=0x2B2D31,
        )
        for member in members_list:
            member_id = int(member.strip("<@>"))
            user = await DB.get_user(ds_id=member_id)
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.experience} опыта```",
            )

        await interaction.response.send_message(embed=embed)


class MessagesCommands(commands.Cog):
    """Command to set nums of users' messages"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @add.sub_command(
        description="Прибавить сообщения любому кол-ву участников (упомянуть через пробел)",
    )
    async def msg(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Adding to several members a certain amount of messages"""
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
                messages=количество,
            )
            if user:
                await DB.update_user(
                    ds_id=user.ds_id,
                    username=user.username,
                    messages=user.messages + количество,
                )
                members_list_values.append(user.messages + количество)
            else:
                members_list_values.append(количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} сообщений было прибавлено к указанным участникам",
            description="Настоящее количество сообщений у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.messages} сообщений```",
            )

        await interaction.response.send_message(embed=embed)

    @remove.sub_command(
        description="Вычесть сообщения любому кол-ву участников (упомянуть через пробел)",
    )
    async def msg(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Adding to several members a certain amount of messages"""
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
                        messages=0,
                    )
                    members_list_values.append(0)
                else:
                    await DB.update_user(
                        ds_id=user.ds_id,
                        username=user.username,
                        messages=user.experience - количество,
                    )
                    members_list_values.append(user.experience - количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} сообщений было вычтено у указанных участников",
            description="Настоящее количество сообщений у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.messages} сообщений```",
            )

        await interaction.response.send_message(embed=embed)

    @set.sub_command(
        description="Установить сообщения любому кол-ву участников (упомянуть через пробел)",
    )
    async def msg(
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
                value=f"```{user.messages} сообщений```",
            )

        await interaction.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ExperienceCommands(bot))
    bot.add_cog(MessagesCommands(bot))
