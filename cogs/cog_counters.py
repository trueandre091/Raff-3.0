from json import loads
from os import getcwd
import disnake
from disnake.ext import commands
from cogs.guilds_functions import guild_sets_check, GDB

FOLDER = getcwd()


class CheckCommands(commands.Cog):
    """Commands to check the statistics for some actions on the guild"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Статистика по некоторым действиям на сервере",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def statistics(self, interaction: disnake.ApplicationCommandInteraction):
        settings = await guild_sets_check(interaction.guild.id)
        if settings is None:
            return

        settings = settings["COUNTERS"]
        guild = interaction.guild
        embed_dict = {
            "title": "Статистика по некоторым действиям на сервере 📋",
            "fields": [],
            "color": 0x2B2D31,
        }
        await interaction.response.send_message(embed=disnake.Embed.from_dict(embed_dict))

        for key, value in settings.items():
            if key == "BOOSTS":
                top = ""
                place = 1
                for k, v in value.items():
                    member = guild.get_member(int(k))
                    top += f"`{place}.` {member.mention} - {v}\n"
                    place += 1
                embed_dict["fields"].append({"name": key, "value": top})
            elif key == "MESSAGES_PREVIOUS_BESTS":
                top = ""
                for k in value:
                    member = guild.get_member(k)
                    top += f"{member.mention} "
                embed_dict["fields"].append({"name": key, "value": top})
            else:
                embed_dict["fields"].append({"name": f"{key}", "value": f"{value}"})

        await interaction.edit_original_response(
            embed=disnake.Embed.from_dict(embed_dict)
        )

    @commands.slash_command(
        description="Изменить статистику",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def set_counter(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        ключ: str,
        значение,
    ):
        settings = await guild_sets_check(interaction.guild.id)
        if settings is None:
            return

        if ключ not in settings["COUNTERS"]:
            await interaction.response.send_message(
                "Данного счётчика не существует", ephemeral=True
            )
            return

        значение = eval(значение)
        if type(значение) is not type(settings["COUNTERS"][ключ]):
            await interaction.response.send_message(
                "Неверный тип значения", ephemeral=True
            )
            return

        settings["COUNTERS"][ключ] = значение

        await GDB.update_guild({"guild_id": interaction.guild.id, "guild_sets": settings})
        await interaction.response.send_message("Изменено")


def setup(bot: commands.Bot):
    bot.add_cog(CheckCommands(bot))
