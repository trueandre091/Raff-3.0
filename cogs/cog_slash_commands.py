import disnake
from disnake.ext import commands


class Commands(commands.Cog):
    """Parent slash commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def add(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def remove(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def set(self, interaction: disnake.ApplicationCommandInteraction):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
