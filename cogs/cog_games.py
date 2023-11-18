from os import getcwd
import disnake
from disnake import app_commands
from disnake.ext import commands
from json import load, dump
from datetime import date
from random import randint

FOLDER = getcwd()
with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Крутануть рулеточку на свои РЕАЛЬНЫЕ очки (/rep)")
    async def roll_win_or_lose(self, inter: disnake.ApplicationCommandInteraction, ставка: int):

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(inter.author.id) in data:
            member_id = inter.author.id

            if ставка > data[str(member_id)] or ставка < 1:

                await inter.response.send_message("Вы поставили больше чем у вас есть, либо меньше 1 💀", delete_after=5, ephemeral=True)

            else:
                lucky = randint(0, 100)
				
                data[str(member_id)] -= ставка

                flag = 1
                if lucky == 100:
                    flag = 3
                    data[str(member_id)] += ставка * 4
                elif lucky >= CONFIG["SETTINGS"]["CHANCE"]:
                    flag = 2
                    data[str(member_id)] += ставка * 2
                elif lucky == 0:
                    flag = 0
                    data[str(member_id)] -= ставка // 2
                member_scores = data[str(member_id)]

                with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
                    dump(data, f)

                embed_dict = {
                    "title": "",
                    "description": f"{inter.author.mention} - `{member_scores}`\nСтавка - `{ставка}`",
                    "color": 0x2b2d31,
                    "author": {
                        "name": "Рулетка на очки 50/50",
                        "icon_url": "https://i.postimg.cc/3JrRXKCz/the-roulette-wheel.jpg"
                    },
                    "footer": {
                        "text": f"{inter.guild.name}",
                        "icon_url": f"{inter.guild.icon.url}"
                    }
                }

                if flag == 1:
                    embed_dict["title"] += "Вам не повезло 🤕"
                    await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
                elif flag == 0:
                    embed_dict["title"] += "Вам КАТЕГОРИЧЕСКИ НЕ повезло 💔"
                    await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
                elif flag == 2:
                    embed_dict["title"] += "Вам повезло, cтавка удвоена 🤑"
                    await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
                elif flag == 3:
                    embed_dict["title"] += "СУПЕРУДАЧА ❤️‍🔥❤️‍🔥❤️‍🔥"
                    await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
        else:

            await inter.response.send_message("У вас 0 очков 💀", delete_after=5, ephemeral=True)

    @roll_win_or_lose.error  # Tell the user when they've got a cooldown
    async def on_test_error(self, interaction: disnake.Interaction, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message("Потерпи 💀", delete_after=5, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Games(bot))
