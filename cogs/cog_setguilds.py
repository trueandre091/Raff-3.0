import disnake
from disnake.ext import commands
from disnake.ui import View, button, select, Button, Modal, TextInput
from disnake.ui import Select, channel_select
from disnake import SelectOption, ModalInteraction
import datetime
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder


async def stud_interaction(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message(
        "Выполняю...", delete_after=0.1, ephemeral=True
    )


class GuildSettings:
    def __init__(self, interaction: disnake.Interaction, settings):
        self.interaction = interaction
        self.gdb = GuildsDBase()
        self.settings = settings

    async def create_home_view(self):
        await self.interaction.edit_original_response(
            content="",
            embed=disnake.Embed.from_dict(create_hello_embed()),
            view=GuildSetsHomeScreenView(self),
        )

    async def create_welcome_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_welcome_cfg()),
            view=GuildSetsGreetView(self, self.settings),
        )

    async def create_farewell_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_farewell_cfg()),
            view=GuildSetsFarewellView(self, self.settings),
        )

    async def create_feedback_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_feedback_cfg()),
            view=GuildSetsFeedbackView(self, self.settings),
        )

    async def create_scores_exp_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(()),
            view=GuildSetsScoresExpView(self, self.settings),
        )

    async def create_games_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(()),
            view=GuildSetsGamesView(self, self.settings),
        )


class GuildSetsHomeScreenView(View):
    def __init__(self, parent):
        super().__init__(timeout=3600)
        self.parent = parent

    @select(
        custom_id="home_screen",
        min_values=1,
        max_values=1,
        placeholder="Что хочешь настроить?",
        options=[
            SelectOption(
                label="Приветствие",
                description="Настрой собственное приветствие",
                emoji="🙋‍♂️",
                value="greetings",
            ),
            SelectOption(
                label="Прощание",
                description="Настрой собственное прощание",
                emoji="👋",
                value="farewell",
            ),
            SelectOption(
                label="Обратная связь",
                description="Получи отзывы и предложения для своего сервера",
                emoji="🤙",
                value="feedback",
            ),
            SelectOption(
                label="Очки и опыт",
                description="Попробуй нашу систему очков и опыта",
                emoji="🪙",
                value="scores_exp",
            ),
            SelectOption(
                label="Игры",
                description="Настрой игры как пожелаешь",
                emoji="🎮",
                value="games",
            ),
            SelectOption(
                label="Ближайшие события",
                description="Показ ближайших событий в чате",
                emoji="📢",
                value="nearest_events",
            ),
            SelectOption(
                label="Модерация",
                description="Настройки модерации",
                emoji="⚙️",
                value="moderation",
            ),
            SelectOption(
                label="Автореакции и автоветки",
                description="Автоматическое управление реакциями и ветками",
                emoji="🌳",
                value="adding_reactions_threads",
            ),
        ],
    )
    async def select_set_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        value = selectMenu.values[0]
        if value == "greetings":
            await stud_interaction(interaction)
            await GuildSettings.create_welcome_view(self.parent)

        elif value == "farewell":
            await stud_interaction(interaction)
            await GuildSettings.create_farewell_view(self.parent)

        elif value == "feedback":
            await stud_interaction(interaction)
            await GuildSettings.create_feedback_view(self.parent)

        elif value == "scores_exp":
            await stud_interaction(interaction)
            await GuildSettings.create_welcome_view(self.parent)

        elif value == "games":
            await stud_interaction(interaction)
            await GuildSettings.create_welcome_view(self.parent)

        elif value == "nearest_events":
            await stud_interaction(interaction)
            await GuildSettings.create_welcome_view(self.parent)

        elif value == "moderation":
            await stud_interaction(interaction)
            await GuildSettings.create_welcome_view(self.parent)

        elif value == "adding_reactions_threads":
            await stud_interaction(interaction)
            await GuildSettings.create_welcome_view(self.parent)


class GuildSetsGreetView(View):
    def __init__(self, parent, settings):
        super().__init__()
        self.parent = parent
        self.settings = settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале приветствовать?",
        min_values=0,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        pass

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, button: Button, interaction: disnake.Interaction):
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_greet_set_callback(
        self, button: Button, interaction: disnake.Interaction
    ):
        await interaction.response.send_modal(GreetModal(self.settings))


class GreetModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        options = [
            TextInput(
                label="Заголовок",
                value=self.settings["WELCOME_SETTINGS"]["EMBED"]["TITLE"],
                min_length=4,
                max_length=75,
                required=True,
                custom_id="title",
            ),
            TextInput(
                label="Сообщение",
                value=self.settings["WELCOME_SETTINGS"]["EMBED"]["DESCRIPTION"],
                style=disnake.TextInputStyle.paragraph,
                max_length=256,
                required=False,
                custom_id="description",
            ),
            TextInput(
                label="Аватарка (дефолтная)",
                value=self.settings["WELCOME_SETTINGS"]["AVATAR_IF_ERROR"],
                required=False,
                custom_id="url_to_ava",
            ),
            TextInput(
                label="Твоя картинка",
                value=self.settings["WELCOME_SETTINGS"]["BACKGROUND_IMAGE"],
                required=False,
                custom_id="background_image",
            ),
            TextInput(
                label="Цвет эмбеда (hex)",
                value=hex(self.settings["WELCOME_SETTINGS"]["EMBED"]["COLOR"]),
                required=False,
                custom_id="color",
            ),
        ]
        super().__init__(title="Настройка приветствий", components=options)

    async def callback(self, interaction: ModalInteraction):
        gdb = GuildsDBase()

        title = interaction.text_values["title"]
        description = interaction.text_values["description"]
        url_to_ava = interaction.text_values["url_to_ava"]
        background_image = interaction.text_values["background_image"]

        self.settings["WELCOME_SETTINGS"]["EMBED"]["TITLE"] = title
        self.settings["WELCOME_SETTINGS"]["EMBED"]["DESCRIPTION"] = description
        self.settings["WELCOME_SETTINGS"]["AVATAR_IF_ERROR"] = url_to_ava
        self.settings["WELCOME_SETTINGS"]["BACKGROUND_IMAGE"] = background_image

        await gdb.update_guild(
            {"guild_id": interaction.guild.id, "guild_sets": self.settings}
        )


class GuildSetsFarewellView(View):
    def __init__(self, parent, settings):
        super().__init__()
        self.parent = parent
        self.settings = settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будем прощаться?",
        min_values=0,
    )
    async def callback(self):
        pass

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, button: Button, interaction: disnake.Interaction):
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(
        self, button: Button, interaction: disnake.Interaction
    ):
        await interaction.response.send_modal(FarewellModal(self.settings))


class FarewellModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        components = [
            TextInput(
                label="Сообщение",
                value=settings["FAREWELL_SETTINGS"]["MESSAGE"],
                max_length=256,
                custom_id="message",
            ),
        ]
        super().__init__(title="Прощание", components=components)


class GuildSetsFeedbackView(View):
    def __init__(self, parent, settings):
        super().__init__()
        self.parent = parent
        self.settings = settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале будем отвечать?",
        min_values=0,
    )
    async def feedback_select_callback(self):
        pass

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, button: Button, interaction: disnake.Interaction):
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_feedback_set_callback(
        self, button: Button, interaction: disnake.Interaction
    ):
        await interaction.response.send_modal(FeedbackModal(self.settings))


class FeedbackModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        components = [
            TextInput(
                label="Сообшение",
                custom_id="message",
            )
        ]
        super().__init__(title="Обратная связь", components=components)


class GuildSetsScoresExpView(View):
    def __init__(self, parent, settings):
        super().__init__()
        self.parent = parent
        self.settings = settings


class GuildSetsGamesView(View):
    def __init__(self, parent, settings):
        super().__init__()
        self.parent = parent
        self.settings = settings


def create_hello_embed():
    embed = {
        "title": "Привет",
        "description": "",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "",
                "value": "Прежде чем начать пользоваться этим ботом и использовать весь функционал его необходимо настроить. "
                "Конечно, ты можешь пропустить этот шаг и вернуться к его настройке позже просто написав '/Настройка бота'\n"
                "(не переживай, настраивать бота могут только администраторы сервера)"
                "Поехали!",
            },
        ],
    }
    return embed


def create_welcome_cfg():
    embed = {
        "title": "Приветствие",
        "description": "Ты можешь поприветствовать новых участников своего сервера!",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Чтобы бот начал приветствовать новых участников необходимо выбрать канал",
            },
            {
                "name": "Кастомное приветствие",
                "value": "Просто нажми на кнопку 'Настроить', введи заголовок, текст своего приветствия и используй! \n"
                "Ты так же можешь упомянуть пользователя, который только что зашёл на сервер. Для этого напиши {member.mention} или {member} на то место, где его требуется упомянуть. \n",
            },
            {
                "name": "Кастомные картинки",
                "value": "Иногда аватарка пользователя может не загрузится или просто отсутствовать. Для таких случае ты можешь выбрать аватар, который будет показываться вместо пользовательского. Просто вставь ссылку из интернета на картинку! \n"
                "Хочешь чтобы твоё приветствие было особенным? Тогда используй свой фон для приветствий!",
            },
        ],
    }
    return embed


def create_farewell_cfg():
    embed = {
        "title": "Прощание",
        "description": "Не забудь попрощаться с теми, кто ушёл!",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Не забудь выбрать канал для прощаний",
            },
            {
                "name": "Кастомное прощание",
                "value": "Ты можешь использовать упоминания как и в приветствиях. На выбор: {member.mention}, {member.nick}, {member.name}, {member}.\n"
                "Ты точно сможешь найти что-то подходящее",
            },
        ],
    }
    return embed


def create_feedback_cfg():
    embed = {
        "title": "Обратная связь",
        "description": "Получай отзывы и жалобы",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Выбери канал для ответа",
            },
            {
                "name": "Кастомное прощание",
                "value": "Ты можешь использовать упоминания как и в приветствиях. На выбор: {member.mention}, {member.nick}, {member.name}, {member}.\n"
                "Ты точно сможешь найти что-то подходящее",
            },
        ],
    }
    return embed


class GuildsManage(commands.Cog):
    """
    This class will manage bot (client) guilds, configure them
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(
        name="настройка_бота", description="Поменять настройки сервера"
    )
    @commands.has_permissions(administrator=True)
    async def set_guild_settings(
        self, interaction: disnake.ApplicationCommandInteraction
    ):
        db = GuildsDBase()
        enc = JsonEncoder()
        data = {
            "guild_id": interaction.guild.id,
            "guild_name": interaction.guild.name,
            "count_members": interaction.guild.member_count,
        }
        guild_sets = await db.add_guild(data)
        if guild_sets:
            set_view = GuildSettings(
                interaction, enc.code_from_json(guild_sets.guild_sets)
            )
            await interaction.send(".")
            await set_view.create_home_view()

    @commands.slash_command(name="add_to_db")
    @commands.is_owner()
    async def add_guild_to_db(self, interaction: disnake.ApplicationCommandInteraction):
        gdb = GuildsDBase()
        data = {
            "guild_id": interaction.guild.id,
            "guild_name": interaction.guild.name,
            "count_members": interaction.guild.member_count,
        }

        for _ in range(5):
            res = await gdb.add_guild(data)
            if res:
                await interaction.response.send_message(f"Success {res}")
                break

    # @commands.Cog.listener()
    # async def on_interaction(self, interaction: disnake.MessageInteraction):
    #     inter = interaction


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
