from os import getcwd

import disnake
from disnake.ext import commands, tasks
from json import load, dump

FOLDER = getcwd()
with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


class CalculateScoresTotal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.calculate_scores_flow.start()
        self.bot = bot

    @tasks.loop(hours=24)
    async def calculate_scores_flow(self):
        with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
            data = load(f)

        data["TOTAL_SCORES"] = data["ADDED_SCORES"] + data["REMOVED_SCORES"]

        with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
            dump(data, f)

    @calculate_scores_flow.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


class CheckCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Статистика по некоторым действиям на сервере",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def statistics(self, inter: disnake.ApplicationCommandInteraction):

        embed_dict = {
            "title": "Статистика по некоторым действиям на сервере 📋",
            "fields": [],
            "color": 0x2b2d31
        }

        await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))

        with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
            data = load(f)

        c = 0
        for key, value in data.items():

            if key == "FAILED_SCORES":
                embed_dict["fields"].append({
                    "name": "Кол-во проигранных очков:",
                    "value": f'{data["FAILED_SCORES"]}'
                })
                c += 1
            elif key == "FAILED_GIF_TRY":
                embed_dict["fields"].append({
                    "name": "Кол-во неудачных попыток отправить гифку:",
                    "value": f'{data["FAILED_GIF_TRY"]}'
                })
                c += 1
            elif key == "ORDERS":
                embed_dict["fields"].append({
                    "name": "Кол-во заказов в рп баре:",
                    "value": f'{data["ORDERS"]}'
                })
                c += 1
            elif key == "LIKERS":
                embed_dict["fields"].append({
                    "name": "Кол-во бустов сервера:",
                    "value": ''
                })

                c1 = 1
                for k, v in data["LIKERS"].items():
                    member = self.bot.get_user(int(k))
                    embed_dict["fields"][c]["value"] += f"`{c1}.` {member.mention} - {v}\n"
                    c1 += 1

                c += 1

        await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))


def setup(bot: commands.Bot):
    bot.add_cog(CalculateScoresTotal(bot))
    bot.add_cog(CheckCommands(bot))
