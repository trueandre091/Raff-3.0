from os import getcwd
import disnake
from disnake.ext import commands
from disnake.ui import Button

import config as cfg
FOLDER = getcwd()


class SendMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["REQUESTS"]["BUTTONS_MESSAGE"]

    @commands.slash_command(
        description="Отправить сообщение для создания запросов",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def buttons(self, interaction: disnake.ApplicationCommandInteraction):
        channel = self.bot.get_channel(self.settings["CHANNEL"])
        embed = disnake.Embed(
            title=self.settings["EMBED"]["TITLE"],
            description=self.settings["EMBED"]["DESCRIPTION"],
            color=self.settings["EMBED"]["COLOR"]
        )

        await channel.send(
            embed=embed,
            components=[
                disnake.ui.Button(
                    label="Сделать запрос",
                    style=disnake.ButtonStyle.success,
                    custom_id="request",
                    emoji="📥"
                )
            ]
        )

        await interaction.response.send_message("Сообщение создано!", ephemeral=True)

    @commands.slash_command(
        description="Ответить на запрос участника",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def ответ_администрации(
            self, interaction: disnake.ApplicationCommandInteraction, запросивший: disnake.Member, ответ: str
    ):
        text_f = ("Если вас не устраивает ответ администрации или вы хотите поговорить с админом подробнее по этому "
                  "запросу - напишите ему в личные сообщения по нику выше")

        embed = disnake.Embed(
            title="Ответ",
            description=ответ,
            color=0x2b2d31
        )
        embed.add_field(
            name="Ответчик",
            value=interaction.author.mention
        )
        embed.set_footer(
            text=text_f
        )

        await запросивший.send(embed=embed)
        await interaction.response.send_message("Ответ отправлен!", ephemeral=True)


class Application(disnake.ui.Modal):
    """Modal application and actions on interaction with it"""
    def __init__(self, bot: commands.Bot):
        self.components = [
            disnake.ui.TextInput(
                label="Тема",
                placeholder="жалоба / вопрос / проблема...",
                custom_id="theme",
                max_length=20
            ),
            disnake.ui.TextInput(
                label="Текст",
                placeholder="хочу пожаловаться на @username, унижает и токсичит... ",
                custom_id="text",
                style=disnake.TextInputStyle.paragraph,
                max_length=100
            )
        ]
        self.bot = bot
        self.settings = cfg.COGS_SETTINGS["REQUESTS"]

        super().__init__(title="Окно запроса", components=self.components)

    async def callback(self, interaction: disnake.ModalInteraction):
        """Sending the messages on interaction with modal application"""
        channel = self.bot.get_channel(self.settings["LOGS_MESSAGE"]["CHANNEL"])

        values = []
        for v in interaction.text_values.values():
            values.append(v)
        embed = disnake.Embed(
            title=f"Новое сообщение 📥",
            description=f"{values[0]}\n```{values[1]}```",
            color=0x2b2d31
        )
        embed.add_field(
            name="Отправитель",
            value=interaction.author.mention,
            inline=False
        )

        await interaction.response.send_message(self.settings["BUTTONS_MESSAGE"]["CALLBACK"], ephemeral=True)

        await channel.send(
            embed=embed,
            components=[
                disnake.ui.Button(
                    label="Отклонить",
                    style=disnake.ButtonStyle.danger,
                    custom_id="deny"
                )
            ]
        )


class Requests(commands.Cog):
    """Reactions on buttons interactions"""
    list_of_messages = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.type == disnake.InteractionType.component:

            if interaction.component.custom_id == "request":
                modal = Application(self.bot)

                await interaction.response.send_modal(modal=modal)

            elif interaction.component.custom_id == "deny":
                button_yes = Button(custom_id='button_yes', label='Да', style=disnake.ButtonStyle.danger)
                button_no = Button(custom_id='button_no', label='Нет', style=disnake.ButtonStyle.green)

                await interaction.response.send_message("Ты уверен?", components=[button_yes, button_no])

            elif interaction.component.custom_id == "button_yes":
                await interaction.message.delete()
                await interaction.response.send_message("Сообщение удалено", ephemeral=True)

            elif interaction.component.custom_id == "button_no":
                await interaction.message.delete()
                await interaction.response.send_message("Сообщение в целости и сохранности", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Requests(bot))
    bot.add_cog(SendMessage(bot))
