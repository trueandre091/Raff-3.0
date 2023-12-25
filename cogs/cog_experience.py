import disnake
from disnake.ext import commands
from random import randint
import math

from cogs.guilds_functions import guild_sets_check, DB, GDB, encoder
from DB.models import Users


async def convert_ex_to_lvl(user: Users, factor: int):
    if user is None:
        return 0

    lvl = math.floor(math.pow(user.experience / factor, 1 / 3))

    return lvl


async def count_experience(message: disnake.Message, settings: dict):
    if not settings["GENERAL_SETTINGS"]["EXPERIENCE"] or message.author.bot:
        return

    settings = settings["COGS_SETTINGS"]["EXPERIENCE"]

    lvl1 = await convert_ex_to_lvl(await DB.get_user({"ds_id": message.author.id}), settings["FACTOR"])

    flag = True
    skip_first_flag = False
    async for msg in message.channel.history(limit=50):
        if message.created_at.minute == msg.created_at.minute and msg.author == message.author and skip_first_flag:
            flag = False
            break
        skip_first_flag = True

    if flag:
        ex = randint(5, 10)

        user = await DB.get_user({"ds_id": message.author.id})
        if not user:
            await DB.add_user(
                {
                    "ds_id": message.author.id,
                    "username": message.author.name,
                    "experience": ex,
                }
            )
        else:
            await DB.update_user(
                {
                    "ds_id": user.ds_id,
                    "username": user.username,
                    "experience": user.experience + ex,
                }
            )

    lvl2 = await convert_ex_to_lvl(await DB.get_user({"ds_id": message.author.id}), settings["FACTOR"])

    if lvl1 != lvl2:
        await message.reply(
            f"{message.author.mention}, поздравляю с {lvl2} уровнем <a:A_applecatrun:992319318425620542>"
        )


class ExperienceCommands(commands.Cog):
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
        """Adding to several members a certain amount of scores"""
        guild = await guild_sets_check(interaction.guild.id, "GENERAL_SETTINGS", "EXPERIENCE")
        if not guild:
            await interaction.response.send_message("Данная функция не включена на сервере", ephemeral=True)
            return

        guild = self.bot.get_guild(interaction.guild.id)
        members_list = участники.split()
        members_list_values = []

        for member in members_list:
            member_id = int(member.strip("<@>"))
            member = guild.get_member(member_id)
            user = await DB.get_user({"ds_id": member_id})
            if user is None:
                await DB.add_user(
                    {
                        "ds_id": member_id,
                        "username": member.name,
                        "experience": количество,
                    }
                )
                members_list_values.append(количество)
            else:
                await DB.update_user(
                    {
                        "ds_id": user.ds_id,
                        "username": user.username,
                        "experience": user.experience + количество,
                    }
                )
                members_list_values.append(user.experience + количество)

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
        guild = await guild_sets_check(interaction.guild.id, "GENERAL_SETTINGS", "EXPERIENCE")
        if not guild:
            await interaction.response.send_message("Данная функция не включена на сервере", ephemeral=True)
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
                        {
                            "ds_id": user.ds_id,
                            "username": user.username,
                            "experience": 0,
                        }
                    )
                    members_list_values.append(0)
                else:
                    await DB.update_user(
                        {
                            "ds_id": user.ds_id,
                            "username": user.username,
                            "experience": user.experience - количество,
                        }
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


def setup(bot: commands.Bot):
    bot.add_cog(ExperienceCommands(bot))
