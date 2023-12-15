from os import getcwd
import disnake
from disnake.ext import commands, tasks
from json import load, dump

FOLDER = getcwd()


async def load_database() -> dict:
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)
    return data


async def dump_database(data: dict) -> None:
    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


class CalculateScoresTotal(commands.Cog):
    """Calculating the total amount of added and removed scores for all the time"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.calculate_scores_flow.start()

    @tasks.loop(hours=24)
    async def calculate_scores_flow(self):
        data = await load_database()
        data["TOTAL_SCORES"] = data["ADDED_SCORES"] + data["REMOVED_SCORES"]
        await dump_database(data)

    @calculate_scores_flow.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


class CheckCommands(commands.Cog):
    """Commands to check the statistics for some actions on the guild"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Статистика по некоторым действиям на сервере",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def statistics(self, interaction: disnake.ApplicationCommandInteraction):
        guild = interaction.guild
        embed_dict = {
            "title": "Статистика по некоторым действиям на сервере 📋",
            "fields": [],
            "color": 0x2b2d31
        }
        await interaction.response.send_message(embed=disnake.Embed.from_dict(embed_dict))

        data = await load_database()
        for key, value in data.items():
            if key == "BOOSTS":
                top = ''
                place = 1
                for k, v in value:
                    member = guild.get_member(int(k))
                    top += f"`{place}.` {member.mention} - {v}\n"
                    place += 1
                embed_dict["fields"].append({"name": "BOOSTS", 'value': top})
            else:
                embed_dict["fields"].append({
                    "name": f"{key}",
                    "value": f"{value}"
                })

        await interaction.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))


def setup(bot: commands.Bot):
    bot.add_cog(CalculateScoresTotal(bot))
    bot.add_cog(CheckCommands(bot))
