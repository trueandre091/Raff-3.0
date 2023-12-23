import disnake
from disnake.ext import commands
from disnake.ui import Modal, TextInput, channel_select


class GuildSetModals(Modal):
    def __init__(self, title, *args, **kwargs):
        select = self.welcome_settings()
        super().__init__(*args, **kwargs, select, title=title)

    @staticmethod
    def welcome_settings():
        select = channel_select(
            min_values=0,
            max_values=1,
            channel_types=disnake.ChannelType.text,
        )
        return select


class GuildsManage(commands.Cog):
    """
    This class will manage bot (client) guilds, configure them
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="Настройки сервера", description="Поменять настройки сервера")
    @commands.has_permissions(administrator=True)
    async def set_guild_settings(self, interaction: disnake.Interaction):
        await interaction.response.send_message(GuildSetModals(title="Настройки сервера"))


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
