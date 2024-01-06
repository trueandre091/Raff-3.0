from loguru import logger
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
from DB.models import Guilds
from typing import Union


async def is_admin(member: disnake.Member) -> bool:
    return member.guild_permissions.administrator


async def get_channel_by_id(
    interaction: disnake.ApplicationCommandInteraction, data: Union[int, list[int]]
) -> str:
    if isinstance(data, int):
        return await interaction.guild.fetch_channel(data)
    elif isinstance(data, list):
        channels = []
        for id in data:
            if id is not None:
                channel: disnake.TextChannel = await interaction.guild.fetch_channel(id)
                channels.append(channel.name)
            else:
                return "не задан"

        return ", ".join(channels)
    else:
        return "не задан"


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


def do_nothing(btn: Button):
    return btn


async def update_sets(self, interaction):
    self.settings[self.route] = self.w_settings

    res = await self.gdb.update_guild(
        {"guild_id": self.parent.interaction.guild.id, "guild_sets": self.settings}
    )
    if res:
        await interaction.response.send_message(
            "Настройки обновлены", delete_after=1, ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Не удалось обновить настройки", delete_after=1, ephemeral=True
        )


async def toggle_set(self, interaction: disnake.Interaction, switch_to: bool):
    if hasattr(self, "s_toggle"):
        self.settings["GENERAL_SETTINGS"][self.toggle][self.s_toggle] = switch_to

    elif hasattr(self, "v_toggle"):
        self.settings["GENERAL_SETTINGS"][self.toggle] = switch_to
        self.settings["GENERAL_SETTINGS"][self.v_toggle] = switch_to

    else:
        self.settings["GENERAL_SETTINGS"][self.toggle] = switch_to

    res = await self.gdb.update_guild(
        {"guild_id": interaction.guild.id, "guild_sets": self.settings}
    )
    if res:
        if switch_to:
            await interaction.response.send_message(
                "Функция включена", delete_after=1, ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Функция выключена", delete_after=1, ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "Не удалось обновить настройки", delete_after=1, ephemeral=True
        )


class GuildSettings:
    def __init__(self, interaction: disnake.Interaction, settings):
        self.interaction: disnake.Interaction = interaction
        self.settings: dict = settings
        self.gdb: GuildsDBase = GuildsDBase()
        self.enc: JsonEncoder = JsonEncoder()

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
        self.settings: dict = parent.settings
        self.gdb: GuildsDBase = parent.gdb

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
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
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

    @button(label="Сбросить", style=disnake.ButtonStyle.danger)
    async def reset_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        self.settings = self.parent.enc.get_default_cfg()
        res = await self.gdb.update_guild(
            {"guild_id": interaction.guild.id, "guild_sets": self.parent.settings}
        )
        if res:
            await interaction.response.send_message(
                "Настройки сброшены успешно!", delete_after=1, ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Не удалось выполнить команду :(", delete_after=1, ephemeral=True
            )


class GuildSetsGreetView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["WELCOME_SETTINGS"]
        self.route: str = "WELCOME_SETTINGS"
        self.toggle: str = "WELCOME"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале приветствовать?",
        min_values=0,
        max_values=1,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.w_settings["CHANNEL"] = selectMenu.values[0].id
        await update_sets(self, interaction)

        logger.debug(f"Channel for greetings  for guild {interaction.guild.name} was updated")

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_greet_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await interaction.response.send_modal(GreetModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await toggle_set(self, interaction, True)

        logger.debug(f"Set WELCOME for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set WELCOME for guild {interaction.guild.name} was switched to False")


class GreetModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings = self.settings["WELCOME_SETTINGS"]
        self.route = "WELCOME_SETTINGS"
        self.gdb = self.parent.gdb
        options = [
            TextInput(
                label="Заголовок",
                value=self.w_settings["EMBED"]["TITLE"],
                min_length=4,
                max_length=75,
                required=True,
                custom_id="title",
            ),
            TextInput(
                label="Сообщение",
                value=self.w_settings["EMBED"]["DESCRIPTION"],
                style=disnake.TextInputStyle.paragraph,
                max_length=256,
                required=False,
                custom_id="description",
            ),
            TextInput(
                label="Аватарка (дефолтная)",
                value=self.w_settings["AVATAR_IF_ERROR"],
                required=False,
                custom_id="url_to_ava",
            ),
            TextInput(
                label="Твоя картинка",
                value=self.w_settings["BACKGROUND_IMAGE"],
                required=False,
                custom_id="background_image",
            ),
            TextInput(
                label="Цвет эмбеда (hex)",
                value=hex(self.w_settings["EMBED"]["COLOR"]),
                required=False,
                custom_id="color",
            ),
        ]
        super().__init__(title="Настройка приветствий", components=options)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.w_settings["EMBED"]["TITLE"] = interaction.text_values["title"]
        self.w_settings["EMBED"]["DESCRIPTION"] = interaction.text_values["description"]
        self.w_settings["AVATAR_IF_ERROR"] = interaction.text_values["url_to_ava"]
        self.w_settings["BACKGROUND_IMAGE"] = interaction.text_values["background_image"]

        await update_sets(self, interaction)

        # await gdb.update_guild(
        #     {"guild_id": interaction.guild.id, "guild_sets": self.settings}
        # )


class GuildSetsFarewellView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["FAREWELL_SETTINGS"]
        self.route: str = "FAREWELL_SETTINGS"
        self.toggle: str = "FAREWELL_SETTINGS"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будем прощаться?",
        min_values=0,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.w_settings["CHANNEL"] = selectMenu.values[0].id
        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return
        await interaction.response.send_modal(FarewellModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set FAREWELL for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set FAREWELL for guild {interaction.guild.name} was switched to False")


class FarewellModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings = self.settings["FAREWELL_SETTINGS"]
        self.route = "FAREWELL_SETTINGS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Сообщение",
                value=self.w_settings["MESSAGE"],
                max_length=256,
                custom_id="message",
            ),
        ]
        super().__init__(title="Прощание", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.w_settings["MESSAGE"] = interaction.text_values["message"]

        await update_sets(self, interaction)


class GuildSetsFeedbackView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS_SETTINGS"]
        self.s_settings: dict = parent.settings["COGS_SETTINGS"]["REQUESTS"]
        self.route: str = "COGS_SETTINGS"
        self.toggle: str = "REQUESTS"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где примем запросы?",
        min_values=0,
    )
    async def channel_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.s_settings["BUTTONS_MESSAGE"]["CHANNEL"] = selectMenu.values[0].id
        self.w_settings["REQUESTS"] = self.s_settings

        await update_sets(self, interaction)

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале будем отвечать?",
        min_values=0,
    )
    async def admin_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.s_settings["ADMIN_CHANNEL"] = selectMenu.values[0].id
        self.w_settings["REQUESTS"] = self.s_settings

        await update_sets(self, interaction)

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где напоминать?",
        min_values=0,
    )
    async def logs_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.s_settings["LOGS_MESSAGE"]["CHANNEL"] = selectMenu.values[0].id
        self.w_settings["REQUESTS"] = self.s_settings

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_feedback_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return
        await interaction.response.send_modal(FeedbackModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set FEEDBACK for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set FEEDBACK for guild {interaction.guild.name} was switched to False")


class FeedbackModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS_SETTINGS"]
        self.s_settings: dict = parent.settings["COGS_SETTINGS"]["REQUESTS"]
        self.route: str = "COGS_SETTINGS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                style=disnake.TextInputStyle.short,
                value=self.s_settings["BUTTONS_MESSAGE"]["EMBED"]["TITLE"],
                label="Заголовок",
                custom_id="title",
            ),
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                value=self.s_settings["BUTTONS_MESSAGE"]["EMBED"]["DESCRIPTION"],
                label="Сообщение",
                custom_id="description",
                max_length=512,
            ),
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Ответ на взаимодействие",
                value=self.s_settings["BUTTONS_MESSAGE"]["CALLBACK"],
                custom_id="set_callback",
                max_length=256,
            ),
            TextInput(
                style=disnake.TextInputStyle.short,
                value=hex(self.s_settings["BUTTONS_MESSAGE"]["EMBED"]["COLOR"]),
                label="Цвет (hex)",
                custom_id="color",
            ),
        ]
        super().__init__(title="Обратная связь", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.s_settings["BUTTONS_MESSAGE"]["EMBED"]["TITLE"] = interaction.text_values["title"]
        self.s_settings["BUTTONS_MESSAGE"]["EMBED"]["DESCRIPTION"] = interaction.text_values[
            "description"
        ]
        self.s_settings["BUTTONS_MESSAGE"]["EMBED"]["COLOR"] = int(
            interaction.text_values["color"], 16
        )
        self.s_settings["BUTTONS_MESSAGE"]["CALLBACK"] = interaction.text_values["set_callback"]

        self.w_settings["REQUESTS"] = self.s_settings

        await update_sets(self, interaction)


class GuildSetsScoresExpView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.toggle = "EXPERIENCE"
        self.v_toggle = "SCORES"
        self.gdb: GuildsDBase = parent.gdb

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set SCORES and EXP for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set SCORES and EXP for guild {interaction.guild.name} was switched to False")


class GuildSetsGamesView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS_SETTINGS"]
        self.s_settings: dict = parent.settings["COGS_SETTINGS"]["GAMES"]
        self.route: str = "COGS_SETTINGS"
        self.s_toggle = "ALL_GAMES"
        self.toggle: str = "GAMES"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах можно играть?",
        max_values=25,
    )
    async def channel_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        channels_id = []
        for value in selectMenu.values:
            channel_id = value.id
            channels_id.append(channel_id)

        self.s_settings["CHANNEL"] = channels_id
        self.w_settings["GAMES"] = self.s_settings

        await update_sets(self, interaction)

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
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
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
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set GAMES for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set GAMES for guild {interaction.guild.name} was switched to False")


class SetBlackJackView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.s_toggle = "BLACKJACK"
        self.toggle = "GAMES"
        self.gdb: GuildsDBase = parent.gdb

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_games_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set BLACKJACK for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set BLACKJACK for guild {interaction.guild.name} was switched to False")


class SetRouletteView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.s_toggle = "ROULETTE"
        self.toggle = "GAMES"
        self.gdb: GuildsDBase = parent.gdb

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_games_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set ROULETTE for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set ROULETTE for guild {interaction.guild.name} was switched to False")


class GuildSetNearestEventsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS_SETTINGS"]
        self.s_settings: dict = parent.settings["COGS_SETTINGS"]["NEAREST_EVENTS"]
        self.route: str = "COGS_SETTINGS"
        self.toggle: str = "NEAREST_EVENTS"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будем рассказывать о событиях?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        self.s_settings["CHANNEL"] = selectMenu.values[0].id

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await interaction.response.send_modal(NearestEventModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set NEAREST_EVENTS for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set NEAREST_EVENTS for guild {interaction.guild.name} was switched to False")


class NearestEventModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS_SETTINGS"]
        self.s_settings: dict = parent.settings["COGS_SETTINGS"]["NEAREST_EVENTS"]
        self.route: str = "COGS_SETTINGS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Категории",
                value=", ".join(self.s_settings["CATEGORIES"]),
                custom_id="categories",
                max_length=512,
            )
        ]
        super().__init__(title="Ближайшие ивенты", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.s_settings["CATEGORIES"] = interaction.text_values["categories"].split(", ")

        self.w_settings["NEAREST_EVENTS"] = self.s_settings

        await update_sets(self, interaction)


class GuildSetModerationView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["MODERATION_SETTINGS"]
        self.route: str = "MODERATION_SETTINGS"
        self.toggle = "MODERATION"
        self.s_toggle = "GIF"
        self.gdb = self.parent.gdb

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах будем следить за участниками?",
        min_values=0,
        max_values=25
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        channels_id = []
        for value in selectMenu.values:
            channels_id.append(value.id)

        self.w_settings["CHANNEL"] = channels_id

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await interaction.response.send_modal(ModerationModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set MODERATION for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set MODERATION for guild {interaction.guild.name} was switched to False")


class ModerationModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["MODERATION_SETTINGS"]
        self.route: str = "MODERATION_SETTINGS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                label="Количество сообщений между гифками",
                value=self.w_settings["GIF"]["MESSAGES_FOR_GIF"],
                custom_id="messages_for_gif",
                max_length=4,
            )
        ]
        super().__init__(title="Настройки модерации", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return

        self.w_settings["GIF"]["MESSAGES_FOR_GIF"] = int(interaction.text_values["messages_for_gif"])

        await update_sets(self, interaction)


class GuildSetReactionsThreadsView:
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.count_options = len(self.settings["ADDING_REACTIONS_THREADS_SETTINGS"])
        self.view_manager = View()

        self.home_screen_btn = Button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)

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
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_home_view(self.parent)

    async def add_option_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
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
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
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
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return
        await stud_interaction(interaction)
        await GuildSettings.create_auto_reactions_threads_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
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
        "title": "чё происходит",
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


async def create_all_sets_embed(data, interaction):
    interaction = interaction
    embed = {
        "title": "Все настройки сервера",
        "description": "Здесь отображаются все настройки и их статус",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Приветствие",
                "value": f"Статус: {'включено' if data['GENERAL_SETTINGS']['WELCOME'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, data['WELCOME_SETTINGS']['CHANNEL'])}\n"
                f"Заголовок: {data['WELCOME_SETTINGS']['EMBED']['TITLE']}\n"
                f"Сообщение: {data['WELCOME_SETTINGS']['EMBED']['DESCRIPTION']}\n"
                f"Цвет: {hex(data['WELCOME_SETTINGS']['EMBED']['COLOR'])}\n"
                f"Автар для пользователей без него: {data['WELCOME_SETTINGS']['AVATAR_IF_ERROR']}\n"
                f"Картинка: {data['WELCOME_SETTINGS']['BACKGROUND_IMAGE']}\n",
            },
            {
                "name": "Прощание",
                "value": f"Статус: {'включено' if data['GENERAL_SETTINGS']['FAREWELL'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, data['FAREWELL_SETTINGS']['CHANNEL'])}\n"
                f"Сообщение: {data['FAREWELL_SETTINGS']['MESSAGE']}\n",
            },
            {
                "name": "Обратная связь",
                "value": f"Статус: {'включено' if data['GENERAL_SETTINGS']['REQUESTS'] else 'выключено'}\n"
                f"Канал (в котором принимаем обращения): {await get_channel_by_id(interaction, data['COGS_SETTINGS']['REQUESTS']['BUTTONS_MESSAGE']['CHANNEL'])}\n"
                f"Канал (в котором обрабатываем обращения): {await get_channel_by_id(interaction, data['COGS_SETTINGS']['REQUESTS']['ADMIN_CHANNEL'])}\n"
                f"Канал (напоминания): {await get_channel_by_id(interaction, data['COGS_SETTINGS']['REQUESTS']['LOGS_MESSAGE']['CHANNEL'])}\n"
                f"Заголовок: {data['COGS_SETTINGS']['REQUESTS']['BUTTONS_MESSAGE']['EMBED']['TITLE']}\n"
                f"Сообщение: {data['COGS_SETTINGS']['REQUESTS']['BUTTONS_MESSAGE']['EMBED']['DESCRIPTION']}\n"
                f"Сообщение при взаимодействии: {data['COGS_SETTINGS']['REQUESTS']['BUTTONS_MESSAGE']['CALLBACK']}\n"
                f"Цвет: {hex(data['COGS_SETTINGS']['REQUESTS']['BUTTONS_MESSAGE']['EMBED']['COLOR'])}\n",
            },
            {
                "name": "Очки и опыт",
                "value": f"Статус: "
                f"{'включено' if data['GENERAL_SETTINGS']['EXPERIENCE'] or data['GENERAL_SETTINGS']['SCORES'] else 'выключено'}\n",
            },
            {
                "name": "Игры",
                "value": f"Все игры: {'включено' if data['GENERAL_SETTINGS']['GAMES']['ALL_GAMES'] else 'выключено'}\n"
                f"Блэкджек: {'включено' if data['GENERAL_SETTINGS']['GAMES']['BLACKJACK'] else 'выключено'}\n"
                f"Рулетка: {'включено' if data['GENERAL_SETTINGS']['GAMES']['ROULETTE'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, data['COGS_SETTINGS']['GAMES']['CHANNEL'])}\n",
            },
            {
                "name": "Ближайшие события",
                "value": f"Статус: {'включено' if data['GENERAL_SETTINGS']['NEAREST_EVENTS'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, data['COGS_SETTINGS']['NEAREST_EVENTS']['CHANNEL'])}\n"
                f"Категории: {', '.join(data['COGS_SETTINGS']['NEAREST_EVENTS']['CATEGORIES'])}",
            },
            {
                "name": "Модерация",
                "value": f"Статус: {'включено' if data['GENERAL_SETTINGS']['MODERATION']['GIF'] else 'выключено'}\n"
                f"Каналы: {await get_channel_by_id(interaction, data['MODERATION_SETTINGS']['CHANNEL'])}\n"
                f"Сообщений до GIF: {data['MODERATION_SETTINGS']['GIF']['MESSAGES_FOR_GIF']}",
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

    @commands.slash_command(name="настройка_бота", description="Поменять настройки сервера")
    async def set_guild_settings(self, interaction: disnake.ApplicationCommandInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            return

        db = GuildsDBase()
        enc = JsonEncoder()
        data = {
            "guild_id": interaction.guild.id,
            "guild_name": interaction.guild.name,
            "count_members": interaction.guild.member_count,
        }
        guild = await db.add_guild(data)
        if guild:
            set_view = GuildSettings(interaction, enc.code_from_json(guild.guild_sets))
            await interaction.send(".")
            await set_view.create_home_view()

    @commands.slash_command(name="текущие_настройки")
    async def current_settings(self, interaction: disnake.ApplicationCommandInteraction):
        if not await is_admin(interaction.author):
            await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
            logger.debug(f"User {interaction.author.name} is not an admin")
            return
        gdb: GuildsDBase = GuildsDBase()
        guild: Guilds = await gdb.get_guild({"guild_id": interaction.guild.id})
        enc: JsonEncoder = JsonEncoder()
        if guild:
            await interaction.response.send_message(
                embed=disnake.Embed.from_dict(
                    await create_all_sets_embed(enc.code_from_json(guild.guild_sets), interaction)
                ),
                ephemeral=True,
            )

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
    async def update_default_sets(self, interaction: disnake.ApplicationCommandInteraction):
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
