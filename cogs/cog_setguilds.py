import disnake
from discord.ext import commands


class GuildsManage(commands.Cog):
    """
    This class will manage bot (client) guilds, configure them
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(description="Поменять настройки сервера")
    @commands.has_permissions(administrator=True)
    async def set_guild_settings(self, interaction: disnake.Interaction):
        pass


class GuildsAAR():
    """
    This class have to append the bot (client) guilds to database
    """
    pass


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
