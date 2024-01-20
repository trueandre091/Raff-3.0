from datetime import datetime
import disnake
from disnake.ext import commands

from cogs.cog_guilds_functions import guild_sets_check, GDB, encoder, is_none
from cogs import counter_functions


class Commands(commands.Cog):
    """Command to make an order"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Сделать заказ в баре")
    async def сделать_заказ(
        self, interaction: disnake.ApplicationCommandInteraction, сообщение: str
    ):
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "ORDERS")
        if await is_none(interaction, settings):
            return

        settings = settings["COGS"]["ORDERS"]

        channel = self.bot.get_channel(settings["CHANNEL"])
        if channel is None:
            await interaction.response.send_message("Канал не найден")
            return

        if interaction.channel.id != channel.id:
            await interaction.response.send_message(
                f"Эта команда может быть использована только в канале {channel.mention}!",
                delete_after=5,
            )

        else:
            await counter_functions.count_orders_counter(interaction.guild.id)

            barmen_role = f"<@&{settings['ROLE']}>"
            embed = disnake.Embed(
                title="Новый заказ 📥",
                description=f"{interaction.author.mention}\n{сообщение}",
                color=0x2B2D31,
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text="Тоже хочешь заказать что-нибудь? Пропиши /сделать_заказ через нашего бота!"
            )

            await interaction.response.send_message(
                f"Доброго времени суток {interaction.author.mention}! Бармен скоро подойдёт 🐥",
                delete_after=10,
            )
            await channel.send(barmen_role, embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
