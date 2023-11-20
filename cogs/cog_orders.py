from datetime import datetime
from json import load
from os import getcwd
import disnake
from disnake.ext import commands

FOLDER = getcwd()

with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Сделать заказ в баре")
    async def заказ(self, inter: disnake.ApplicationCommandInteraction, сообщение: str):
        channel = self.bot.get_channel(CONFIG["CHANNEL_RPBAR"])
        barmen_role = "<@&829082636705595433>"

        if inter.channel.id != CONFIG["CHANNEL_RPBAR"]:

            await inter.send(f"Эта команда может быть использована только в канале {channel.mention}!")

        else:

            embed = disnake.Embed(
                title="Новый заказ 📥",
                description=f"{inter.author.mention}\n{сообщение}",
                color=0x2b2d31,
                timestamp=datetime.now()
            )

            embed.set_footer(text="Тоже хочешь заказать что-нибудь? Пропиши /заказ через нашего бота!")

            await channel.send(barmen_role, embed=embed)
            await inter.send(
                f"Доброго времени суток {inter.author.mention}! Бармен скоро подойдёт 🐥",
                delete_after=20.0
            )


def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
