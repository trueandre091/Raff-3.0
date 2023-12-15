from os import getcwd
import disnake
from disnake.ext import commands, tasks
from disnake.ui import Button

import config as cfg
FOLDER = getcwd()


class RequestsReminder(commands.Cog):
    message_id = 0

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.irresponsible_requests.start()
        self.settings = cfg.COGS_SETTINGS["REQUESTS"]

    @tasks.loop(hours=12)
    async def irresponsible_requests(self):
        list_of_requests = Requests.list_of_messages
        guild = self.bot.get_guild(cfg.GUILD_ID)
        channel = guild.get_channel(self.settings["ADMIN_CHANNEL"])
        channel_requests = guild.get_channel(self.settings["LOGS_MESSAGE"]["CHANNEL"])
        embed = disnake.Embed(
            title="Непросмотренные запросы 📫",
            color=0x2b2d31
        )

        place = 1
        for request_id in list_of_requests:
            message = await channel_requests.fetch_message(request_id)
            name = message.embeds[-1].to_dict()["description"].split('\n')[0]
            value = message.jump_url

            embed.add_field(name=f"{place}. {name}", value=value)
            place += 1

        try:
            message = await channel.fetch_message(RequestsReminder.message_id)
            await message.delete()
        except disnake.errors.NotFound:
            pass

        await channel.send(embed=embed)
        async for message in channel.history(limit=1):
            RequestsReminder.message_id = message.id

    @irresponsible_requests.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


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
                    label="Сообщение не прочитано",
                    style=disnake.ButtonStyle.danger,
                    emoji='✖️',
                    custom_id="read"
                ),
                disnake.ui.Button(
                    label="Отклонить",
                    style=disnake.ButtonStyle.danger,
                    custom_id="deny"
                )
            ]
        )
        async for msg in channel.history(limit=1):
            if "Новое сообщение 📥" in msg.embeds[-1].to_dict()["title"]:
                Requests.list_of_messages.append(msg.id)


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

            ###############################################################################

            elif interaction.component.custom_id == "deny":
                button_yes = Button(custom_id='button_yes', label='Да', style=disnake.ButtonStyle.danger)
                button_no = Button(custom_id='button_no', label='Нет', style=disnake.ButtonStyle.green)

                await interaction.response.send_message("Ты уверен?", components=[button_yes, button_no])

            elif interaction.component.custom_id == "read":
                try:
                    Requests.list_of_messages.remove(interaction.message.id)
                except ValueError:
                    pass

                await interaction.response.send_message("Помечено", ephemeral=True)
                await interaction.message.edit(
                    components=[
                        disnake.ui.Button(
                            label="Сообщение прочитано",
                            style=disnake.ButtonStyle.grey,
                            emoji='✔️',
                            custom_id="unread"
                        )
                    ]
                )

            elif interaction.component.custom_id == "unread":
                Requests.list_of_messages.append(interaction.message.id)

                await interaction.response.send_message("Помечено", ephemeral=True)
                await interaction.message.edit(
                    components=[
                        disnake.ui.Button(
                            label="Сообщение не прочитано",
                            style=disnake.ButtonStyle.danger,
                            emoji='✖️',
                            custom_id="read"
                        ),
                        disnake.ui.Button(
                            label="Отклонить",
                            style=disnake.ButtonStyle.danger,
                            custom_id="deny"
                        )
                    ]
                )

            ###############################################################################

            elif interaction.component.custom_id == "button_yes":
                message = await interaction.channel.fetch_message(interaction.message.reference.message_id)

                await message.delete()
                await interaction.message.delete()
                await interaction.response.send_message("Сообщение удалено", ephemeral=True)

            elif interaction.component.custom_id == "button_no":
                await interaction.message.delete()
                await interaction.response.send_message("Сообщение в целости и сохранности", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Requests(bot))
    bot.add_cog(SendMessage(bot))
    bot.add_cog(RequestsReminder(bot))
