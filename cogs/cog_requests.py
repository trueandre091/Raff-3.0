from os import getcwd
import disnake
from disnake.ext import commands
from json import load

FOLDER = getcwd()

with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


class SendMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Отправить сообщение для создания запросов",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def buttons(self, inter: disnake.ApplicationCommandInteraction):
        channel = self.bot.get_channel(992788044514082876)
        await inter.response.send_message("Сообщение для запросов создано!", ephemeral=True)
        embed = disnake.Embed(
            title="Служба поддержки 📟",
            description="При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации и " +
                        "оставить отзыв о качестве поддержки, нажав на соответствующие кнопки ниже",
            color=0x2b2d31
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


class Application(disnake.ui.Modal):

    def __init__(self, bot: commands.Bot):
        self.components = [
            disnake.ui.TextInput(
                label="Тема запроса",
                placeholder="жалоба / вопрос / проблема...",
                custom_id="Тема",
                max_length=20
            ),
            disnake.ui.TextInput(
                label="Текст",
                placeholder="хочу пожаловаться на @username, унижает и токсичит... ",
                custom_id="Текст",
                style=disnake.TextInputStyle.paragraph,
                max_length=100
            )
        ]
        self.bot = bot

        super().__init__(title="Окно запроса", components=self.components)

    async def callback(self, inter: disnake.ModalInteraction):
        channel = self.bot.get_channel(CONFIG["CHANNEL_LOGS"])

        values = []
        for v in inter.text_values.values():
            values.append(v)

        embed = disnake.Embed(
            title=f"Новый запрос 📥",
            description=f"{values[0]}\n```{values[1]}```",
            color=0x2b2d31
        )
        embed.add_field(
            name="Отправитель",
            value=inter.author.mention,
            inline=False
        )

        await inter.response.send_message("Запрос успешно отправлен! <a:A_heart1:993383076363239444>\n*Ждите ответ от "
                                          "администрации, он будет отправлен вам в личные сообщения*", ephemeral=True)
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
    """Where will be requests operations"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if "component" in interaction.type:

            if interaction.component.custom_id == "request":

                modal = Application(self.bot)
                await interaction.response.send_modal(modal=modal)

            elif interaction.component.custom_id == "deny":

                await interaction.message.delete()

    @commands.slash_command(
        description="Ответить на запрос участника",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def адм_ответ(self, interaction, отправитель: disnake.Member, ответ: str):
        text_f = ("Если вас не устраивает ответ администрации или вы хотите поговорить с админом подробнее по этому "
                  "запросу - напишите ему в личные сообщения по нику выше")

        embed = disnake.Embed(
            title="Ответ на ваш запрос",
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

        await отправитель.send(embed=embed)
        await interaction.response.send_message("Ответ отправлен!", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Requests(bot))
    bot.add_cog(SendMessage(bot))
