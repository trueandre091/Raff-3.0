import disnake
from disnake.ext import commands, tasks
from disnake.ui import Button

from cogs.guilds_functions import guild_sets_check, find_guilds_by_param, encoder, GDB


class Request:
    list_of_objects = []

    def __init__(
        self,
        guild_id: int,
        author: disnake.Member,
        theme: str,
        text: str,
        message_id: int = None,
    ):
        self.guild_id = guild_id
        self.author = author
        self.theme = theme
        self.text = text
        self.flag = False
        self.message_id = message_id


class RequestsReminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.irresponsible_requests.start()

    @tasks.loop(hours=1)
    async def irresponsible_requests(self):
        guilds = await find_guilds_by_param(self.bot, "GENERAL_SETTINGS", "REQUESTS")

        for settings in guilds:
            guild = self.bot.get_guild(settings["GUILD_ID"])
            settings = settings["COGS_SETTINGS"]["REQUESTS"]

            channel = guild.get_channel(settings["ADMIN_CHANNEL"])
            channel_logs = guild.get_channel(settings["LOGS_MESSAGE"]["CHANNEL"])
            if channel is None or channel_logs is None:
                continue

            embed = disnake.Embed(title="Непросмотренные запросы 📫", color=0x2B2D31)

            place = 1
            for request in Request.list_of_objects:
                if request.guild_id == guild.id and not request.read:
                    message = await channel_logs.fetch_message(request.message_id)
                    name = message.embeds[-1].to_dict()["description"].split("\n")[0]
                    value = message.jump_url

                    embed.add_field(name=f"{place}. {name}", value=value)
                    place += 1

            async for msg in channel.history(limit=50):
                try:
                    if "Непросмотренные запросы" in msg.embeds[-1].to_dict()["title"]:
                        await msg.delete()
                except:
                    pass
            await channel.send(embed=embed)

    @irresponsible_requests.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


class SendMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Отправить сообщение для создания запросов",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def buttons(self, interaction: disnake.ApplicationCommandInteraction):
        """Sending the message to make requests"""
        settings = await guild_sets_check(
            interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
        )
        if settings is None:
            await interaction.response.send_message(
                "Данная функция отключена на сервере", ephemeral=True
            )
            return

        settings = settings["COGS_SETTINGS"]["REQUESTS"]

        embed = disnake.Embed(
            title=settings["BUTTONS_MESSAGE"]["EMBED"]["TITLE"],
            description=settings["BUTTONS_MESSAGE"]["EMBED"]["DESCRIPTION"],
            color=settings["BUTTONS_MESSAGE"]["EMBED"]["COLOR"],
        )

        await interaction.channel.send(
            embed=embed,
            components=[
                disnake.ui.Button(
                    label="Сделать запрос",
                    style=disnake.ButtonStyle.success,
                    custom_id="request",
                    emoji="📥",
                )
            ],
        )

        await interaction.response.send_message("Сообщение создано!", ephemeral=True)

    @commands.slash_command(
        description="Ответить на запрос участника",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def ответ_администрации(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        запросивший: disnake.Member,
        ответ: str,
    ):
        """Answering to the request (not relevant now)"""
        settings = await guild_sets_check(
            interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
        )
        if settings is None:
            await interaction.response.send_message(
                "Данная функция отключена на сервере", ephemeral=True
            )
            return

        text_f = (
            "Если вас не устраивает ответ администрации или вы хотите поговорить с админом подробнее по этому "
            "запросу - напишите ему в личные сообщения по нику выше"
        )

        embed = disnake.Embed(title="Ответ", description=ответ, color=0x2B2D31)
        embed.add_field(name="Ответчик", value=interaction.author.mention)
        embed.set_footer(text=text_f)

        await запросивший.send(embed=embed)
        await interaction.response.send_message("Ответ отправлен!", ephemeral=True)


class Application1(disnake.ui.Modal):
    """Modal application and actions on interaction with it"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        super().__init__(
            title="Окно запроса",
            components=[
                disnake.ui.TextInput(
                    label="Тема",
                    placeholder="жалоба / вопрос / проблема...",
                    custom_id="theme",
                    max_length=20,
                ),
                disnake.ui.TextInput(
                    label="Текст",
                    placeholder="хочу пожаловаться на @username, унижает и токсичит... ",
                    custom_id="request_text",
                    style=disnake.TextInputStyle.paragraph,
                    max_length=100,
                ),
            ],
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        """Sending the messages on interaction with modal application"""
        guild = await GDB.get_guild({"guild_id": interaction.guild.id})
        settings = encoder.code_from_json(guild.guild_sets)["COGS_SETTINGS"]["REQUESTS"]

        values = []
        for v in interaction.text_values.values():
            values.append(v)

        obj = Request(interaction.guild.id, interaction.author, values[0], values[1])
        channel = self.bot.get_channel(settings["LOGS_MESSAGE"]["CHANNEL"])

        embed = disnake.Embed(
            title=f"Новое сообщение 📥",
            description=f"{values[0]}\n```{values[1]}```",
            color=0x2B2D31,
        )
        embed.add_field(
            name="Отправитель", value=interaction.author.mention, inline=False
        )

        await interaction.response.send_message(
            settings["BUTTONS_MESSAGE"]["CALLBACK"], ephemeral=True
        )
        await channel.send(
            embed=embed,
            components=[
                disnake.ui.Button(
                    label="Сообщение не прочитано",
                    style=disnake.ButtonStyle.danger,
                    emoji="✖️",
                    custom_id="read",
                ),
                disnake.ui.Button(
                    label="Отклонить",
                    style=disnake.ButtonStyle.danger,
                    custom_id="deny",
                ),
                disnake.ui.Button(
                    label="Ответить", style=disnake.ButtonStyle.grey, custom_id="answer"
                ),
            ],
        )
        async for msg in channel.history(limit=1):
            if "Новое сообщение 📥" in msg.embeds[-1].to_dict()["title"]:
                obj.message_id = msg.id
                Request.list_of_objects.append(obj)


class Application2(disnake.ui.Modal):
    """Modal application and actions on interaction with it"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        super().__init__(
            title="Окно ответа",
            components=[
                disnake.ui.TextInput(
                    label="Ответ",
                    placeholder="было принято решение человека забанить...",
                    custom_id="answer",
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Пояснение",
                    placeholder="такое решение было принято так как человек...",
                    custom_id="explanation",
                    style=disnake.TextInputStyle.paragraph,
                    max_length=200,
                ),
            ],
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        values = []
        for v in interaction.text_values.values():
            values.append(v)

        text_f = (
            "Если вас не устраивает ответ администрации или вы хотите поговорить с админом подробнее по этому "
            "запросу - напишите ему в личные сообщения по нику выше"
        )

        embed = disnake.Embed(
            title="Ответ", description=f"{values[0]}\n```{values[1]}```", color=0x2B2D31
        )
        embed.add_field(name="Ответчик", value=interaction.author.mention)
        embed.set_footer(text=text_f)

        flag = True
        for obj in Request.list_of_objects:
            if obj.message_id == interaction.message.id:
                await obj.author.send(embed=embed)
                flag = False
                await interaction.response.send_message("Ответ отправлен", ephemeral=True)
                Request.list_of_objects.remove(obj)
                try:
                    for request in Request.list_of_objects:
                        if request.message_id == interaction.message.id:
                            request.read = True
                except ValueError:
                    pass

                await interaction.message.edit(
                    components=[
                        disnake.ui.Button(
                            custom_id="answered",
                            label="Ответ отправлен",
                            style=disnake.ButtonStyle.green,
                        )
                    ]
                )

        if flag:
            await interaction.response.send_message("Участник не найден", ephemeral=True)


class RequestInteractions(commands.Cog):
    """Reactions on buttons interactions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.type == disnake.InteractionType.component:
            if interaction.component.custom_id == "request":
                settings = await guild_sets_check(
                    interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
                )
                if settings is None:
                    await interaction.response.send_message(
                        "Данная функция отключена на сервере", ephemeral=True
                    )
                    return

                modal = Application1(self.bot)

                await interaction.response.send_modal(modal=modal)

            ###############################################################################

            elif interaction.component.custom_id == "read":
                settings = await guild_sets_check(
                    interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
                )
                if settings is None:
                    await interaction.response.send_message(
                        "Данная функция отключена на сервере", ephemeral=True
                    )
                    return

                for request in Request.list_of_objects:
                    if request.message_id == interaction.message.id:
                        request.read = True

                await interaction.response.send_message("Отмечено", ephemeral=True)
                await interaction.message.edit(
                    components=[
                        disnake.ui.Button(
                            label="Сообщение прочитано",
                            style=disnake.ButtonStyle.grey,
                            emoji="✔️",
                            custom_id="unread",
                        ),
                        disnake.ui.Button(
                            label="Ответить",
                            style=disnake.ButtonStyle.grey,
                            custom_id="answer",
                        ),
                    ]
                )

            elif interaction.component.custom_id == "unread":
                settings = await guild_sets_check(
                    interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
                )
                if settings is None:
                    await interaction.response.send_message(
                        "Данная функция отключена на сервере", ephemeral=True
                    )
                    return

                for request in Request.list_of_objects:
                    if request.message_id == interaction.message.id:
                        request.read = False

                await interaction.response.send_message("Отмечено", ephemeral=True)
                await interaction.message.edit(
                    components=[
                        disnake.ui.Button(
                            label="Сообщение не прочитано",
                            style=disnake.ButtonStyle.danger,
                            emoji="✖️",
                            custom_id="read",
                        ),
                        disnake.ui.Button(
                            label="Отклонить",
                            style=disnake.ButtonStyle.danger,
                            custom_id="deny",
                        ),
                        disnake.ui.Button(
                            label="Ответить",
                            style=disnake.ButtonStyle.grey,
                            custom_id="answer",
                        ),
                    ]
                )

            ###############################################################################

            elif interaction.component.custom_id == "deny":
                settings = await guild_sets_check(
                    interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
                )
                if settings is None:
                    await interaction.response.send_message(
                        "Данная функция отключена на сервере", ephemeral=True
                    )
                    return

                button_yes = Button(
                    custom_id="button_yes", label="Да", style=disnake.ButtonStyle.danger
                )
                button_no = Button(
                    custom_id="button_no", label="Нет", style=disnake.ButtonStyle.green
                )

                await interaction.response.send_message(
                    "Ты уверен?", components=[button_yes, button_no]
                )

            elif interaction.component.custom_id == "button_yes":
                message = await interaction.channel.fetch_message(
                    interaction.message.reference.message_id
                )

                await message.delete()
                await interaction.message.delete()
                await interaction.response.send_message(
                    "Сообщение удалено", ephemeral=True
                )

            elif interaction.component.custom_id == "button_no":
                await interaction.message.delete()
                await interaction.response.send_message(
                    "Сообщение в целости и сохранности", ephemeral=True
                )

            ###############################################################################

            elif interaction.component.custom_id == "answer":
                settings = await guild_sets_check(
                    interaction.guild.id, "GENERAL_SETTINGS", "REQUESTS"
                )
                if settings is None:
                    await interaction.response.send_message(
                        "Данная функция отключена на сервере", ephemeral=True
                    )
                    return

                modal = Application2(self.bot)

                await interaction.response.send_modal(modal=modal)


def setup(bot: commands.Bot):
    bot.add_cog(RequestInteractions(bot))
    bot.add_cog(SendMessage(bot))
    bot.add_cog(RequestsReminder(bot))
