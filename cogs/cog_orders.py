from datetime import datetime
from json import load, dump
from os import getcwd
import disnake
from disnake.ext import commands

import config as cfg
from cogs import counter_functions
FOLDER = getcwd()


class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["ORDERS"]

    @commands.slash_command(description="Сделать заказ в баре")
    async def сделать_заказ(self, interaction: disnake.ApplicationCommandInteraction, сообщение: str):
        channel = self.bot.get_channel(self.settings["CHANNEL"])

        if interaction.channel.id != channel.id:

            await interaction.response.send_message(
                f"Эта команда может быть использована только в канале {channel.mention}!", delete_after=5
            )

        else:

            await counter_functions.count_orders_counter()

            barmen_role = f"<@&{self.settings['BARMEN_ROLE']}>"
            embed = disnake.Embed(
                title="Новый заказ 📥",
                description=f"{interaction.author.mention}\n{сообщение}",
                color=0x2b2d31,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Тоже хочешь заказать что-нибудь? Пропиши /заказ через нашего бота!")

            await interaction.response.send_message(
                f"Доброго времени суток {interaction.author.mention}! Бармен скоро подойдёт 🐥",
                delete_after=10
            )
            await channel.send(barmen_role, embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
