import disnake
from disnake.ext import commands
from disnake.ui import View, button, select, Button, Modal, TextInput
from disnake.ui import Select, channel_select
from disnake import SelectOption, ModalInteraction
import datetime
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder
import random
from DB.config_default import GUILD_CONFIG


async def is_admin(member: disnake.Member) -> bool:
    return member.guild_permissions.administrator


async def stud_interaction(interaction: disnake.ApplicationCommandInteraction):
    phrases = [
        "Выполняю...",
        "Подчиняюсь...",
        "Секунду...",
        "Реализую...",
        "Инициализирую...",
        "Загружаю...",
        "Ищу...",
        "Завариваю кофе...",
        "Подготавливаю...",
        "Придумываю шутку...",
        "Разумеется",
        "Да, мой господин",
        "Есть сэр!",
        "Так точно!",
    ]
    await interaction.response.send_message(
        random.choice(phrases), delete_after=0.01, ephemeral=True
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
            embed=disnake.Embed.from_dict(create_welcome_embed()),
            view=GuildSetsGreetView(self),
        )

    async def create_farewell_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_farewell_embed()),
            view=GuildSetsFarewellView(self),
        )

    async def create_feedback_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_feedback_embed()),
            view=GuildSetsFeedbackView(self),
        )

    async def create_scores_exp_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_scores_exp_embed())),
            view=GuildSetsScoresExpView(self),
        )

    async def create_games_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_games_embed())),
            view=GuildSetsGamesView(self),
        )

    async def create_blackjack_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_blackjack_embed())),
            view=SetBlackJackView(self),
        )

    async def create_roulette_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_roulette_embed())),
            view=SetRouletteView(self),
        )

    async def create_nearest_events_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_nearest_event_embed())),
            view=GuildSetNearestEventsView(self),
        )

    async def create_moderation_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_moderation_embed())),
            view=GuildSetModerationView(self),
        )

    async def create_auto_reactions_threads_view(self):
        await GuildSetReactionsThreadsView(self).send_view()


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
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

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
            await GuildSettings.create_scores_exp_view(self.parent)

        elif value == "games":
            await stud_interaction(interaction)
            await GuildSettings.create_games_view(self.parent)

        elif value == "nearest_events":
            await stud_interaction(interaction)
            await GuildSettings.create_nearest_events_view(self.parent)

        elif value == "moderation":
            await stud_interaction(interaction)
            await GuildSettings.create_moderation_view(self.parent)

        elif value == "adding_reactions_threads":
            await stud_interaction(interaction)
            await GuildSettings.create_auto_reactions_threads_view(self.parent)

    @button(label="Сохранить", style=disnake.ButtonStyle.green)
    async def save_callback(self, button: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Сбросить", style=disnake.ButtonStyle.danger)
    async def reset_callback(self, button: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class GuildSetsGreetView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале приветствовать?",
        min_values=0,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_greet_set_callback(
        self, btn: Button, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

        await interaction.response.send_modal(GreetModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class GreetModal(Modal):
    def __init__(self, parent):
        self.settings = parent.settings
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
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
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
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будем прощаться?",
        min_values=0,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(
        self, btn: Button, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await interaction.response.send_modal(FarewellModal(self.settings))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class FarewellModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        components = [
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Сообщение",
                value=self.settings["FAREWELL_SETTINGS"]["MESSAGE"],
                max_length=256,
                custom_id="message",
            ),
        ]
        super().__init__(title="Прощание", components=components)


class GuildSetsFeedbackView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале будем отвечать?",
        min_values=0,
    )
    async def feedback_select_callback(
        self, selectMenu: Select, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_feedback_set_callback(
        self, btn: Button, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await interaction.response.send_modal(FeedbackModal(self.settings))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class FeedbackModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        components = [
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Сообщение",
                custom_id="message",
                max_length=512,
            )
        ]
        super().__init__(title="Обратная связь", components=components)


class GuildSetsScoresExpView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class GuildSetsGamesView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @select(
        custom_id="select_game",
        min_values=1,
        max_values=1,
        placeholder="Что хочешь настроить?",
        options=[
            SelectOption(
                label="BlackJack",
                description="Настрой BlackJack",
                emoji="♠️",
                value="blackjack",
            ),
            SelectOption(
                label="Рулетка",
                description="Настрой рулетку",
                emoji="♠️",
                value="roulette",
            ),
        ],
    )
    async def select_game_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        value = selectMenu.values[0]

        if value == "blackjack":
            await stud_interaction(interaction)
            await GuildSettings.create_blackjack_view(self.parent)

        elif value == "roulette":
            await stud_interaction(interaction)
            await GuildSettings.create_roulette_view(self.parent)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class SetBlackJackView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале будем играть?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_games_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class SetRouletteView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале будем играть?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_games_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class GuildSetNearestEventsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будем рассказывать о событиях?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(
        self, btn: Button, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await interaction.response.send_modal(NearestEventModal(self.settings))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class NearestEventModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        components = [
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Категории",
                value=", ".join(
                    self.settings["COGS_SETTINGS"]["NEAREST_EVENTS"]["CATEGORIES"]
                ),
                custom_id="message",
                max_length=512,
            )
        ]
        super().__init__(title="Ближайшие ивенты", components=components)


class GuildSetModerationView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах будем следить за участниками?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(
        self, btn: Button, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await interaction.response.send_modal(ModerationModal(self.settings))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class ModerationModal(Modal):
    def __init__(self, settings):
        self.settings = settings
        components = [
            TextInput(
                label="Количество сообщений между гифками",
                value=self.settings["MODERATION_SETTINGS"]["GIF"]["MESSAGES_FOR_GIF"],
                custom_id="message",
                max_length=4,
            )
        ]
        super().__init__(title="Настройки модерации", components=components)


class GuildSetReactionsThreadsView:
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.count_options = len(self.settings["ADDING_REACTIONS_THREADS_SETTINGS"])
        self.view_manager = View()

        self.home_screen_btn = Button(
            label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger
        )

        self.add_option_btn = Button(label="+", style=disnake.ButtonStyle.green)

        self.view_manager.add_item(self.home_screen_btn)
        self.view_manager.add_item(self.add_option_btn)

        for i in range(1, self.count_options + 1):
            btn = Button(label=str(i))
            btn.callback = self.option_callback
            self.view_manager.add_item(btn)

        self.home_screen_btn.callback = self.home_screen_callback
        self.add_option_btn.callback = self.add_option_callback

    async def home_screen_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    async def add_option_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await self.parent.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_option_embed()),
            view=OptionThreadView(self.parent),
        )

    async def send_view(self):
        await self.parent.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_reactions_threads_embed()),
            view=self.view_manager,
        )

    async def option_callback(self, interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return


class OptionThreadView(View):
    def __init__(self, parent, option=None):
        super().__init__()
        self.parent = parent
        self.option = option

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах будем следить за участниками?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await stud_interaction(interaction)
        await GuildSettings.create_auto_reactions_threads_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(
        self, btn: Button, interaction: disnake.Interaction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return
        await interaction.response.send_modal(OptionThreadModal(self.option))


class OptionThreadModal(Modal):
    def __init__(self, option):
        self.option = option
        components = [
            TextInput(
                label="Код реакции",
                value="" if self.option is None else self.option["REACTIONS"],
                custom_id="reacts",
            )
        ]
        super().__init__(title="Настройка реакций", components=components)


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


def create_welcome_embed():
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


def create_farewell_embed():
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


def create_feedback_embed():
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


def create_scores_exp_embed():
    embed = {
        "title": "Очки и опыт",
        "description": "Система очков и опыта",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
        ],
    }

    return embed


def create_games_embed():
    embed = {
        "title": "Игры",
        "description": "Настрой игры",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой их отдельно",
                "value": "Выбери игру, которую хочешь настроить",
            },
        ],
    }

    return embed


def create_blackjack_embed():
    embed = {
        "title": "BlackJack",
        "description": "Настрой игры",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой Blackjack",
                "value": "Выбери канал, в котором будет разрешено играть",
            },
        ],
    }

    return embed


def create_roulette_embed():
    embed = {
        "title": "Roulette",
        "description": "Настрой игры",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой рулетку",
                "value": "Выбери канал, в котором будет разрешено играть",
            },
        ],
    }

    return embed


def create_nearest_event_embed():
    embed = {
        "title": "Ближайшие события",
        "description": "Настрой отображение событий",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой категории для событий",
                "value": "Выбери канал, в котором будет разрешено играть",
            },
        ],
    }

    return embed


def create_moderation_embed():
    embed = {
        "title": "Модерация",
        "description": "Настрой модерацию",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой категории для событий",
                "value": "Выбери канал, в котором будет разрешено играть",
            },
        ],
    }

    return embed


def create_reactions_threads_embed():
    embed = {
        "title": "Автореакции и автоветки",
        "description": "Настрой вот это вот",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой категории для событий",
                "value": "Выбери канал, в котором будет разрешено играть",
            },
        ],
    }

    return embed


def create_option_embed():
    embed = {
        "title": "Пездец чё происходит",
        "description": "Настрой вот это вот",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки",
                "value": "Нажми 'Вкл', если хочешь использовать систему очков и опыта на своём сервере",
            },
            {
                "name": "Настрой категории для событий",
                "value": "Выбери канал, в котором будет разрешено играть",
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
    async def set_guild_settings(
        self, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message(
                "You are not an admin😲", ephemeral=True
            )
            return

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

    @commands.slash_command(name="update_default_sets")
    @commands.is_owner()
    async def update_default_sets(
        self, interaction: disnake.ApplicationCommandInteraction
    ):
        gdb = GuildsDBase()
        enc = JsonEncoder()
        res = await gdb.update_guild(
            {
                "guild_id": interaction.guild.id,
                "guild_sets": enc.code_to_json(GUILD_CONFIG),
            }
        )

        if res:
            await interaction.response.send_message(
                f"Successfully update guild {interaction.guild.name}"
            )


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
