from loguru import logger

import disnake
from disnake.ext import commands
from disnake.ui import View, button, select, Button, Modal, TextInput
from disnake.ui import Select, channel_select, role_select
from disnake import SelectOption, ModalInteraction

import datetime
from bot import update, settings
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder
from DB.config_default import GUILD_CONFIG
from DB.models import Guilds

import random


async def is_admin(interaction: disnake.Interaction) -> bool:
    admin: bool = interaction.author.guild_permissions.administrator
    if not admin:
        await interaction.response.send_message("У тебя не хватает прав😛", ephemeral=True)
        logger.debug(f"User {interaction.author.name} is not an admin")
        return False
    else:
        return True


async def get_channel_by_id(
    interaction: disnake.ApplicationCommandInteraction, data: int | list[int]
) -> str:
    if isinstance(data, int):
        return await interaction.guild.fetch_channel(data)
    elif isinstance(data, list):
        channels = []
        if len(data) != 0:
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


async def update_sets(self, interaction, switch_to=None):
    self.settings["COGS"][self.route] = self.w_settings

    res = await self.gdb.update_guild(
        guild_id=self.parent.interaction.guild.id, guild_sets=self.settings
    )
    if res:
        if switch_to is None:
            await interaction.response.send_message(
                "Настройки обновлены", delete_after=1, ephemeral=True
            )
        elif not switch_to:
            await interaction.response.send_message(
                "Функция выключена", delete_after=1, ephemeral=True
            )
        elif switch_to:
            await interaction.response.send_message(
                "Функция включена", delete_after=1, ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "Не удалось обновить настройки", delete_after=1, ephemeral=True
        )


async def toggle_set_easy(self, interaction: disnake.Interaction):
    fn_num = int(str(interaction.component.custom_id).strip("fn_"))
    switch_to = True
    if "success" in str(interaction.component.style):
        switch_to = False
    elif "danger" in str(interaction.component.style):
        switch_to = True

    key0 = "GENERAL"
    try:
        if type(self.keys[str(fn_num)]) is list:
            key1 = self.keys[str(fn_num)][0]
            key2 = self.keys[str(fn_num)][1]
            self.parent[str(interaction.guild.id)].settings[key0][key1][key2] = switch_to
        else:
            key1 = self.keys[str(fn_num)]
            self.parent[str(interaction.guild.id)].settings[key0][key1] = switch_to
    except KeyError:
        await interaction.response.send_message(
            "Сообщение устарело", ephemeral=True, delete_after=5
        )

    res = await self.gdb.update_guild(
        {
            "guild_id": interaction.guild.id,
            "guild_sets": self.parent[str(interaction.guild.id)].settings,
        }
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
        await GuildSettings.create_general_view(self.parent[str(interaction.guild.id)])
    else:
        await interaction.response.send_message(
            "Не удалось обновить настройки", delete_after=1, ephemeral=True
        )

        logger.debug(
            f"Set {self.keys[str(fn_num)]} for guild {interaction.guild.name} was switched to False"
        )


async def toggle_set(self, interaction: disnake.Interaction, switch_to: bool):
    if hasattr(self, "s_toggle"):
        self.settings["GENERAL"][self.toggle][self.s_toggle] = switch_to

    elif hasattr(self, "v_toggle"):
        self.settings["GENERAL"][self.toggle] = switch_to
        self.settings["GENERAL"][self.v_toggle] = switch_to

    else:
        self.settings["GENERAL"][self.toggle] = switch_to

    res = await self.gdb.update_guild(guild_id=interaction.guild.id, guild_sets=self.settings)
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
    def __init__(self, interaction: disnake.Interaction, guild_sets):
        self.interaction: disnake.Interaction = interaction
        self.settings: dict = guild_sets
        self.gdb: GuildsDBase = GuildsDBase()
        self.enc: JsonEncoder = JsonEncoder()

    async def create_home_view(self):
        await self.interaction.edit_original_response(
            content="",
            embed=disnake.Embed.from_dict(create_hello_embed()),
            view=GuildSetsHomeScreenView(self),
        )

    async def create_general_view(self):
        data = await self.gdb.get_guild(guild_id=self.interaction.guild.id)
        components = GuildSetsGeneralView(self).components
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(
                create_general_embed(self.enc.code_from_json(data.guild_sets))
            ),
            components=components,
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

    async def create_autoupdate_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_autoupdate_embed()),
            view=AutoupdateSetsView(self),
        )

    async def create_autoupdate_scores_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_autoupdate_scores_embed()),
            view=ScoresUpdateSetsView(self),
        )

    async def create_autoupdate_messages_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_autoupdate_messages_embed()),
            view=MessagesUpdateSetsView(self),
        )

    async def create_scores_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_scores_embed())),
            view=ScoresSetsView(self),
        )

    async def create_exp_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict((create_experience_embed())),
            view=ExpSetsView(self),
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
        options = await get_channel_by_id(
            self.interaction, [*self.settings["COGS"]["REACTIONS_THREADS"].keys()]
        )
        await GuildSetReactionsThreadsView(self, options).send_view()

    async def create_autoroles_view(self):
        await AutoRolesSetsView(self).send_view(),


class GuildSetsGeneralView:
    def __init__(self, parent):
        self.parent = parent
        self.settings: dict = parent.settings
        self.gdb: GuildsDBase = parent.gdb
        self.components = []

        self.components.append(
            Select(
                custom_id="home_screen",
                min_values=1,
                max_values=1,
                placeholder="Что хочешь настроить?",
                options=[
                    SelectOption(
                        label="Приветствие",
                        description="Настрой приветствие бота",
                        emoji="👋",
                        value="greetings",
                    ),
                    SelectOption(
                        label="Прощание",
                        description="Настрой прощание бота",
                        emoji="💀",
                        value="farewell",
                    ),
                    SelectOption(
                        label="Таблицы лидеров с автоматическим обновлением",
                        description="Быстрый способ оценить своё место в рейтинге",
                        emoji="📊",
                        value="autoupdate",
                    ),
                    SelectOption(
                        label="Система запросов к администрации",
                        description="Настрой систему для получения запросов от участников по любому вопросу",
                        emoji="📟",
                        value="feedback",
                    ),
                    # SelectOption(
                    #     label="Система очков и Система опыта",
                    #     description="Удобные системы оценивания участников",
                    #     emoji="📀",
                    #     value="scores_exp",
                    # ),
                    SelectOption(
                        label="Игры",
                        description="Включение и настройка игр",
                        emoji="🎰",
                        value="games",
                    ),
                    SelectOption(
                        label="Доска ближайших событий",
                        description="Настройка доски ближайших событий с авто обновлением",
                        emoji="📢",
                        value="nearest_events",
                    ),
                    SelectOption(
                        label="Система опыта",
                        description="Удобная система оценки активности участников",
                        emoji="⌛",
                        value="experience",
                    ),
                    SelectOption(
                        label="Система очков",
                        description="Удобная система поощрения участников за их активность",
                        emoji="⚖️",
                        value="scores",
                    ),
                    SelectOption(
                        label="Модерация",
                        description="Настройки модерации",
                        emoji="⚔️",
                        value="moderation",
                    ),
                    SelectOption(
                        label="Автореакции и Автоветки",
                        description="Автоматическое создание реакций и веток к сообщениям",
                        emoji="♾️",
                        value="adding_reactions_threads",
                    ),
                    SelectOption(
                        label="Автороли", description="напиши чёнить", emoji="🏧", value="roles"
                    ),
                ],
            )
        )

        place = 1
        for fn, value in parent.settings["GENERAL"].items():
            if fn == "PASSWORD":
                continue
            print(fn, value)
            if type(value) is bool:
                self.components.append(
                    Button(
                        label=f"{place}",
                        custom_id=f"fn_{place}",
                        style=disnake.ButtonStyle.green if value else disnake.ButtonStyle.red,
                    )
                )
                place += 1
            elif type(value) is dict:
                for k, v in value.items():
                    if k == "ALL_GAMES":
                        continue
                    self.components.append(
                        Button(
                            label=f"{place}",
                            custom_id=f"fn_{place}",
                            style=disnake.ButtonStyle.green if v else disnake.ButtonStyle.red,
                        )
                    )
                    place += 1

        self.components.append(
            Button(
                label=f"Назад",
                emoji="🔙",
                custom_id=f"back",
                style=disnake.ButtonStyle.red,
            )
        )


class GuildSetsHomeScreenView(View):
    def __init__(self, parent):
        super().__init__(timeout=3600)
        self.parent = parent
        self.settings: dict = parent.settings
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    # @select(
    #     custom_id="home_screen",
    #     min_values=1,
    #     max_values=1,
    #     placeholder="Что хочешь настроить?",
    #     options=["check"],
    # )
    # async def select_set_callback(
    #     self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    # ):
    #     if not await is_admin(interaction):
    #         return
    #
    #     value = selectMenu.values[0]
    #     if value == "greetings":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_welcome_view(self.parent)
    #
    #     elif value == "farewell":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_farewell_view(self.parent)
    #
    #     elif value == "feedback":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_feedback_view(self.parent)
    #
    #     elif value == "scores_exp":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_scores_exp_view(self.parent)
    #
    #     elif value == "games":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_games_view(self.parent)
    #
    #     elif value == "nearest_events":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_nearest_events_view(self.parent)
    #
    #     elif value == "moderation":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_moderation_view(self.parent)
    #
    #     elif value == "adding_reactions_threads":
    #         await stud_interaction(interaction)
    #         await GuildSettings.create_auto_reactions_threads_view(self.parent)

    @button(label="Начать", style=disnake.ButtonStyle.gray)
    async def start_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Сбросить", style=disnake.ButtonStyle.danger)
    async def reset_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        enc = self.enc
        self.parent.settings = enc.get_default_cfg()
        self.parent.settings["GUILD_ID"] = interaction.guild.id
        res = await self.gdb.update_guild(
            guild_id=interaction.guild.id,
            guild_sets=enc.code_to_json(self.parent.settings),
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
        self.w_settings: dict = parent.settings["COGS"]["WELCOME"]
        self.route: str = "WELCOME"
        self.toggle: str = "WELCOME"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале?",
        min_values=0,
        max_values=1,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        values = selectMenu.values
        self.w_settings["CHANNEL"] = values[0].id if values is not None else None
        await update_sets(self, interaction)

        logger.debug(f"Channel for greetings for guild {interaction.guild.name} was updated")

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Настроить")
    async def open_greet_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(GreetModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, True)

        logger.debug(f"Set WELCOME for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set WELCOME for guild {interaction.guild.name} was switched to False")


class GreetModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings = self.settings["COGS"]["WELCOME"]
        self.route = "WELCOME"
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
                label="Текст",
                value=self.w_settings["EMBED"]["DESCRIPTION"],
                style=disnake.TextInputStyle.paragraph,
                max_length=256,
                required=False,
                custom_id="description",
            ),
            TextInput(
                label="Ссылка на аватарку, если у участника её нет",
                value=self.w_settings["EMBED"]["AVATAR_IF_ERROR"],
                required=False,
                custom_id="url_to_ava",
            ),
            TextInput(
                label="Фоновая картинка",
                value=self.w_settings["EMBED"]["IMAGE"],
                required=False,
                custom_id="background_image",
            ),
            TextInput(
                label="Цвет боковой полоски Embed (hex)",
                value=hex(self.w_settings["EMBED"]["COLOR"]),
                required=False,
                custom_id="color",
            ),
        ]
        super().__init__(title="Настройка Приветствий", components=options)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        self.w_settings["EMBED"]["TITLE"] = interaction.text_values["title"]
        self.w_settings["EMBED"]["DESCRIPTION"] = interaction.text_values["description"]
        self.w_settings["EMBED"]["AVATAR_IF_ERROR"] = interaction.text_values["url_to_ava"]
        self.w_settings["EMBED"]["IMAGE"] = interaction.text_values["background_image"]
        self.w_settings["EMBED"]["COLOR"] = int(interaction.text_values["color"], 16)

        await update_sets(self, interaction)


class GuildSetsFarewellView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["FAREWELL"]
        self.route: str = "FAREWELL"
        self.toggle: str = "FAREWELL"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале?",
        min_values=0,
        max_values=1,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        values = selectMenu.values
        self.w_settings["CHANNEL"] = values[0].id if values is not None else None
        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(FarewellModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set FAREWELL for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set FAREWELL for guild {interaction.guild.name} was switched to False")


class FarewellModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings = self.settings["COGS"]["FAREWELL"]
        self.route = "FAREWELL"
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
        super().__init__(title="Настройка Прощаний", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        self.w_settings["MESSAGE"] = interaction.text_values["message"]

        await update_sets(self, interaction)


class AutoupdateSetsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["AUTOUPDATE"]
        self.route: str = "AUTOUPDATE"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будут сообщения?",
        min_values=0,
    )
    async def admin_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        values = selectMenu.values

        self.w_settings["CHANNEL"] = values[0].id if values is not None else None

        await update_sets(self, interaction)

    @select(
        placeholder="Выбери для отдельной настройки",
        custom_id="autoupdate_select",
        min_values=1,
        max_values=1,
        options=[
            SelectOption(
                label="Очки",
                description="Таблица лидеров по очкам за месяц",
                emoji="⚖️",
                value="scores",
            ),
            SelectOption(
                label="Сообщения",
                description="Таблица лидеров по сообщениям за неделю",
                emoji="💬",
                value="messages",
            ),
        ],
    )
    async def select_autoupdate_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
            return

        value = selectMenu.values[0]

        if value == "scores":
            await stud_interaction(interaction)
            await GuildSettings.create_autoupdate_scores_view(self.parent)

        elif value == "messages":
            await stud_interaction(interaction)
            await GuildSettings.create_autoupdate_messages_view(self.parent)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)


class ScoresUpdateSetsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["AUTOUPDATE"]
        self.route: str = "AUTOUPDATE"
        self.toggle: str = "AUTOUPDATE"
        self.s_toggle: str = "SCORES"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_autoupdate_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(AutoUpdateModal(self.parent, "scores"))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(
            f"Set AUTOUPDATE SCORES for guild {interaction.guild.name} was switched to True"
        )

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(
            f"Set AUTOUPDATE SCORES for guild {interaction.guild.name} was switched to False"
        )


class MessagesUpdateSetsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["AUTOUPDATE"]
        self.route: str = "AUTOUPDATE"
        self.toggle: str = "AUTOUPDATE"
        self.s_toggle: str = "MESSAGES"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_autoupdate_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(AutoUpdateModal(self.parent, "messages"))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(
            f"Set AUTOUPDATE SCORES for guild {interaction.guild.name} was switched to True"
        )

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(
            f"Set AUTOUPDATE SCORES for guild {interaction.guild.name} was switched to False"
        )


class AutoUpdateModal(Modal):
    def __init__(self, parent, type_modal):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["AUTOUPDATE"]
        self.route: str = "AUTOUPDATE"
        self.gdb = self.parent.gdb

        self.type_modal: str = type_modal

        if type_modal == "scores":
            self.modal_title = "Очки"
            self.components = [
                TextInput(
                    style=disnake.TextInputStyle.short,
                    value=self.w_settings["SCORES"]["LIMIT"],
                    label="тута чёто напиши",
                    custom_id="scores",
                ),
            ]
        elif type_modal == "messages":
            self.modal_title = "Сообщения"
            self.components = [
                TextInput(
                    style=disnake.TextInputStyle.short,
                    value=self.w_settings["MESSAGES"]["LIMIT"],
                    label="тута чёто напиши",
                    custom_id="messages",
                ),
            ]

        super().__init__(title=self.modal_title, components=self.components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        if interaction.custom_id == "scores":
            self.w_settings["SCORES"]["LIMIT"] = interaction.text_values["scores"]
        elif interaction.custom_id == "messages":
            self.w_settings["MESSAGES"]["LIMIT"] = interaction.text_values["messages"]

        await update_sets(self, interaction)


class GuildSetsFeedbackView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["REQUESTS"]
        self.route: str = "REQUESTS"
        self.toggle: str = "REQUESTS"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Куда отправлять запросы?",
        min_values=0,
    )
    async def admin_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        values = selectMenu.values

        self.w_settings["CHANNELS"]["LOGS"] = values[0].id if values is not None else None

        await update_sets(self, interaction)

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будем напоминать?",
        min_values=0,
    )
    async def logs_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        values = selectMenu.values

        self.w_settings["CHANNELS"]["REMINDER"] = values[0].id if values is not None else None

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Настроить")
    async def open_feedback_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(FeedbackModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set FEEDBACK for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set FEEDBACK for guild {interaction.guild.name} was switched to False")


class FeedbackModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["REQUESTS"]
        self.route: str = "REQUESTS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                style=disnake.TextInputStyle.short,
                value=self.w_settings["MESSAGE"]["EMBED"]["TITLE"],
                label="Заголовок",
                custom_id="title",
            ),
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                value=self.w_settings["MESSAGE"]["EMBED"]["DESCRIPTION"],
                label="Текст",
                custom_id="description",
                max_length=512,
            ),
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Ответ на создание запроса",
                value=self.w_settings["MESSAGE"]["CALLBACK"],
                custom_id="set_callback",
                max_length=256,
            ),
            TextInput(
                style=disnake.TextInputStyle.short,
                value=hex(self.w_settings["MESSAGE"]["EMBED"]["COLOR"]),
                label="Цвет боковой полоски Embed (hex)",
                custom_id="color",
            ),
        ]
        super().__init__(title="Обратная связь", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        self.w_settings["MESSAGE"]["EMBED"]["TITLE"] = interaction.text_values["title"]
        self.w_settings["MESSAGE"]["EMBED"]["DESCRIPTION"] = interaction.text_values["description"]
        self.w_settings["MESSAGE"]["EMBED"]["COLOR"] = int(interaction.text_values["color"], 16)
        self.w_settings["MESSAGE"]["CALLBACK"] = interaction.text_values["set_callback"]

        await update_sets(self, interaction)


class ScoresSetsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.toggle: str = "SCORES"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set SCORES for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set SCORES for guild {interaction.guild.name} was switched to False")


class ExpSetsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.toggle: str = "EXPERIENCE"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set EXP for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set EXP for guild {interaction.guild.name} was switched to False")


class GuildSetsGamesView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["GAMES"]
        self.route: str = "GAMES"
        self.s_toggle = "ALL_GAMES"
        self.toggle: str = "GAMES"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах доступны игры?",
        min_values=0,
        max_values=25,
    )
    async def channel_select_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        if selectMenu.values is not None:
            channels_id = []
            for value in selectMenu.values:
                channel_id = value.id
                channels_id.append(channel_id)
        else:
            channels_id = None

        self.w_settings["CHANNELS"] = channels_id

        await update_sets(self, interaction)

    @select(
        custom_id="select_game",
        min_values=1,
        max_values=1,
        placeholder="Какую игру настроить?",
        options=[
            SelectOption(
                label="BlackJack",
                emoji="♠️",
                value="blackjack",
            ),
            SelectOption(
                label="Рулетка",
                emoji="🎲",
                value="roulette",
            ),
        ],
    )
    async def select_game_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
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
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set GAMES for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set GAMES for guild {interaction.guild.name} was switched to False")


class SetBlackJackView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.toggle = "GAMES"
        self.s_toggle = "BLACKJACK"
        self.gdb: GuildsDBase = parent.gdb

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_games_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set BLACKJACK for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set BLACKJACK for guild {interaction.guild.name} was switched to False")


class SetRouletteView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.toggle = "GAMES"
        self.s_toggle = "ROULETTE"
        self.gdb: GuildsDBase = parent.gdb

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_games_view(self.parent)

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set ROULETTE for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set ROULETTE for guild {interaction.guild.name} was switched to False")


class GuildSetNearestEventsView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["NEAREST_EVENTS"]
        self.route: str = "NEAREST_EVENTS"
        self.toggle: str = "NEAREST_EVENTS"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="Где будет сообщение?",
        min_values=0,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
            return

        values = selectMenu.values
        self.w_settings["CHANNEL"] = values[0].id if values is not None else None

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(NearestEventModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set NEAREST_EVENTS for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set NEAREST_EVENTS for guild {interaction.guild.name} was switched to False")


class NearestEventModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["NEAREST_EVENTS"]
        self.route: str = "COGS_SETTINGS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                style=disnake.TextInputStyle.paragraph,
                label="Категории",
                value=", ".join(self.w_settings["CATEGORIES"]),
                custom_id="categories",
                max_length=512,
            )
        ]
        super().__init__(title="Настройка Доски ближайших событий", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        self.w_settings["CATEGORIES"] = interaction.text_values["categories"].split(", ")

        await update_sets(self, interaction)


class GuildSetModerationView(View):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["MODERATION"]
        self.route: str = "MODERATION"
        self.toggle = "MODERATION"
        self.s_toggle = "GIF"
        self.gdb = self.parent.gdb

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах будем следить за участниками?",
        min_values=0,
        max_values=25,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
            return
        if selectMenu.values is not None:
            channels_id = []
            for value in selectMenu.values:
                channels_id.append(value.id)
        else:
            channels_id = None

        self.w_settings["CHANNELS"] = channels_id

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    @button(label="Настроить")
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await interaction.response.send_modal(ModerationModal(self.parent))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=True)

        logger.debug(f"Set MODERATION for guild {interaction.guild.name} was switched to True")

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await toggle_set(self, interaction, switch_to=False)

        logger.debug(f"Set MODERATION for guild {interaction.guild.name} was switched to False")


class ModerationModal(Modal):
    def __init__(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["MODERATION"]
        self.route: str = "MODERATION"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                label="Количество сообщений между гифками",
                value=self.w_settings["GIF"]["DELAY"],
                custom_id="messages_for_gif",
                max_length=4,
            )
        ]
        super().__init__(title="Настройки модерации", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        self.w_settings["GIF"]["DELAY"] = int(interaction.text_values["messages_for_gif"])

        await update_sets(self, interaction)


class AutoRolesSetsView:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings: dict = parent.settings
        self.w_settings: dict = self.settings["COGS"]["SPECIAL"]
        self.toggle: str = "ROLES"
        self.gdb: GuildsDBase = parent.gdb
        self.enc: JsonEncoder = parent.enc

        self.view_manager = View()
        self.home_screen_btn = Button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
        self.add_option_btn = Button(label="+", style=disnake.ButtonStyle.green)

        self.home_screen_btn.callback = self.home_screen_callback
        self.add_option_btn.callback = self.add_option_callback

        self.view_manager.add_item(self.home_screen_btn)
        self.view_manager.add_item(self.add_option_btn)

        index = 0

        for i in self.w_settings["ROLES"]:
            if i["TITLE"] is None:
                btn = Button(label=index, custom_id=index)
                index += 1
            else:
                btn = Button(label=i["TITLE"], custom_id=i["TITLE"])
                
            btn.callback = self.role_btn_callback
            self.view_manager.add_item(btn)

    async def send_view(self):
        await self.parent.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_roles_embed()),
            view=self.view_manager,
        )

    async def home_screen_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    async def add_option_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await self.parent.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_roles_option_embed()),
            view=RolesOptionSetsView(self.parent),
        )

    async def role_btn_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)

        id = interaction.component.custom_id
        for option in self.w_settings["ROLES"]:
            if option["TITLE"] == id:
                await self.parent.interaction.edit_original_response(
                    embed=disnake.Embed.from_dict(create_roles_option_embed()),
                    view=RolesOptionSetsView(self.parent, option=option),
                )


class RolesOptionSetsView(View):
    def __init__(self, parent, option=None):
        super().__init__()
        self.parent = parent
        self.option = option
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["SPECIAL"]
        self.route: str = "SPECIAL"
        self.gdb = self.parent.gdb

    @role_select(
        placeholder="тута чёта нада",
        custom_id="roles_have",
        min_values=1,
    )
    async def roles_have_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
            return

        if self.option is None:
            self.w_settings[selectMenu.values[0].id] = {
                "ROLES_HAVE": [None],
                "ROLES_GET": [None],
                "TITLE": None,
            }
        else:
            self.w_settings[selectMenu.values[0].id] = self.w_settings.pop(self.option)

        values = selectMenu.values
        self.option = values[0].id if values is not None else None

        self.parent.settings["COGS"]["REACTIONS_THREADS"] = self.w_settings

        await update_sets(self, interaction)

    @role_select(
        placeholder="тута чёта нада",
        custom_id="roles_get",
        min_values=1,
    )
    async def roles_get_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
            return

        if self.option is None:
            self.w_settings[selectMenu.values[0].id] = {"REACTIONS": [], "THREAD": False}
        else:
            self.w_settings[selectMenu.values[0].id] = self.w_settings.pop(self.option)

        values = selectMenu.values
        self.option = values[0].id if values is not None else None

        self.parent.settings["COGS"]["REACTIONS_THREADS"] = self.w_settings

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_autoroles_view(self.parent)

    @button(label="Настроить")
    async def open_reaction_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is None:
            await interaction.response.send_message(
                "Сначала выбери канал", delete_after=1, ephemeral=True
            )
        else:
            await interaction.response.send_modal(OptionThreadModal(self.parent, self.option))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is None:
            await interaction.response.send_message(
                "Сначала выбери канал", delete_after=1, ephemeral=True
            )
        else:
            self.w_settings[self.option]["THREAD"] = True
            await update_sets(self, interaction, switch_to=True)

            logger.debug(
                f"Set THREAD for channel {self.option} for guild {interaction.guild.name} was switched to True"
            )

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is None:
            await interaction.response.send_message(
                "Сначала выбери канал", delete_after=1, ephemeral=True
            )
        else:
            self.w_settings[self.option]["THREAD"] = False
            await update_sets(self, interaction, switch_to=False)

            logger.debug(
                f"Set THREAD for channel {self.option} for guild {interaction.guild.name} was switched to False"
            )

    @button(label="Удалить", style=disnake.ButtonStyle.danger)
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is not None:
            del self.w_settings[self.option]
            await update_sets(self, interaction)
        await GuildSettings.create_autoroles_view(self.parent)


class RoleOptionModal(Modal):
    def __init__(self, parent, option):
        self.parent = parent
        self.option = option
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["SPECIAL"]
        self.route: str = "SPECIAL"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                label="title",
                value=" ".join(self.w_settings[self.option]["REACTIONS"]),
                custom_id="title",
            )
        ]
        super().__init__(title="Настройка реакций", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        # Change this
        self.w_settings["ROLES"] = interaction.text_values["title"]

        await update_sets(self, interaction)


class GuildSetReactionsThreadsView:
    def __init__(self, parent, options):
        self.parent = parent
        self.options = options
        self.settings = parent.settings
        self.channels_id = [*self.settings["COGS"]["REACTIONS_THREADS"].keys()]
        self.toggle = "REACTIONS_THREADS"
        self.view_manager = View()

        self.home_screen_btn = Button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)

        self.add_option_btn = Button(label="+", style=disnake.ButtonStyle.green)

        self.home_screen_btn.callback = self.home_screen_callback
        self.add_option_btn.callback = self.add_option_callback
        self.view_manager.add_item(self.home_screen_btn)
        self.view_manager.add_item(self.add_option_btn)

        if self.options != "не задан":
            self.options = self.options.split(", ")
        else:
            self.options = []

        for i in range(len(self.channels_id)):
            btn = Button(label=self.options[i], custom_id=self.channels_id[i])
            btn.callback = self.option_callback
            self.view_manager.add_item(btn)

    async def home_screen_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_general_view(self.parent)

    async def add_option_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction):
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

    async def option_callback(self, interaction: disnake.Interaction):
        if not await is_admin(interaction):
            return

        option = interaction.component.custom_id
        channel = interaction.component.label
        await stud_interaction(interaction)
        await self.parent.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_option_embed(channel)),
            view=OptionThreadView(self.parent, option=option),
        )


class OptionThreadView(View):
    def __init__(self, parent, option=None):
        super().__init__()
        self.parent = parent
        self.option = option
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["REACTIONS_THREADS"]
        self.route: str = "REACTIONS_THREADS"
        self.gdb = self.parent.gdb

    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каких каналах будем добавлять реакции и ветки?",
        min_values=1,
        max_values=1,
    )
    async def select_callback(
        self, selectMenu: Select, interaction: disnake.ApplicationCommandInteraction
    ):
        if not await is_admin(interaction):
            return

        if self.option is None:
            self.w_settings[selectMenu.values[0].id] = {"REACTIONS": [], "THREAD": False}
        else:
            self.w_settings[selectMenu.values[0].id] = self.w_settings.pop(self.option)

        values = selectMenu.values
        self.option = values[0].id if values is not None else None

        self.parent.settings["COGS"]["REACTIONS_THREADS"] = self.w_settings

        await update_sets(self, interaction)

    @button(label="Назад", emoji="🔙", style=disnake.ButtonStyle.danger)
    async def to_back_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        await stud_interaction(interaction)
        await GuildSettings.create_auto_reactions_threads_view(self.parent)

    @button(label="Настроить")
    async def open_reaction_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is None:
            await interaction.response.send_message(
                "Сначала выбери канал", delete_after=1, ephemeral=True
            )
        else:
            await interaction.response.send_modal(OptionThreadModal(self.parent, self.option))

    @button(label="Вкл", style=disnake.ButtonStyle.green)
    async def enable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is None:
            await interaction.response.send_message(
                "Сначала выбери канал", delete_after=1, ephemeral=True
            )
        else:
            self.w_settings[self.option]["THREAD"] = True
            await update_sets(self, interaction, switch_to=True)

            logger.debug(
                f"Set THREAD for channel {self.option} for guild {interaction.guild.name} was switched to True"
            )

    @button(label="Выкл", style=disnake.ButtonStyle.danger)
    async def disable_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is None:
            await interaction.response.send_message(
                "Сначала выбери канал", delete_after=1, ephemeral=True
            )
        else:
            self.w_settings[self.option]["THREAD"] = False
            await update_sets(self, interaction, switch_to=False)

            logger.debug(
                f"Set THREAD for channel {self.option} for guild {interaction.guild.name} was switched to False"
            )

    @button(label="Удалить", style=disnake.ButtonStyle.danger)
    async def open_farewell_set_callback(self, btn: Button, interaction: disnake.Interaction):
        do_nothing(btn)
        if not await is_admin(interaction):
            return

        if self.option is not None:
            del self.w_settings[self.option]
            await update_sets(self, interaction)
        await GuildSettings.create_auto_reactions_threads_view(self.parent)


class OptionThreadModal(Modal):
    def __init__(self, parent, option):
        self.parent = parent
        self.option = option
        self.settings = parent.settings
        self.w_settings: dict = parent.settings["COGS"]["REACTIONS_THREADS"]
        self.route: str = "REACTIONS_THREADS"
        self.gdb = self.parent.gdb
        components = [
            TextInput(
                label="Код реакции",
                value=" ".join(self.w_settings[self.option]["REACTIONS"]),
                custom_id="reacts",
            )
        ]
        super().__init__(title="Настройка реакций", components=components)

    async def callback(self, interaction: ModalInteraction):
        if not await is_admin(interaction):
            return

        reacts = interaction.text_values["reacts"]

        if " " in reacts:
            reacts = reacts.split(" ")
        else:
            reacts = [reacts]

        self.w_settings[self.option]["REACTIONS"] = reacts

        await update_sets(self, interaction)


def create_hello_embed():
    embed = {
        "title": "Привет! 📍",
        "description": "Прежде чем начать пользоваться этим ботом и использовать весь функционал его необходимо "
        "настроить. \n\nКонечно, ты можешь пропустить этот шаг и вернуться к его настройке позже, "
        "просто написав `/настройка_бот`\n(не переживай, настраивать бота могут только администраторы "
        "сервера)",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    return embed


def create_general_embed(data: dict):
    on = "**Включено**"
    off = "**Выключено**"
    embed = {
        "title": "Статус функций",
        "description": f"**1.** Приветствие - {on if data['GENERAL']['WELCOME'] else off}\n\n"
        f"**2.** Прощание - {on if data['GENERAL']['FAREWELL'] else off}\n\n"
        f"**3.** Модерация: {[f'{k} - {on if v else off}' for k, v in data['GENERAL']['MODERATION'].items()]}\n\n"
        f"**4.** | **5.** Автотопы: Сообщения | Очки - {on if data['GENERAL']['AUTOUPDATE']['MESSAGES'] else off}, "
        f"{on if data['GENERAL']['AUTOUPDATE']['SCORES'] else off}\n\n"
        f"**6.** Доска ближайших событий - {on if data['GENERAL']['NEAREST_EVENTS'] else off}\n\n"
        f"**7.** Опыт (уровни) - {on if data['GENERAL']['EXPERIENCE'] else off}\n\n"
        f"**8.** | **9.** Игры: Блекджек | Рулетка - {on if data['GENERAL']['GAMES']['BLACKJACK'] else off}, "
        f"{on if data['GENERAL']['GAMES']['ROULETTE'] else off}\n\n"
        f"**10.** Заказы (недоступно) - {on if data['GENERAL']['ORDERS'] else off}\n\n"
        f"**11.** Запросы к администрации - {on if data['GENERAL']['REQUESTS'] else off}\n\n"
        f"**12.** Очки - {on if data['GENERAL']['SCORES'] else off}\n\n"
        f"**13.** Подсчёт бустеров на мониторингах (недоступно) - {on if data['GENERAL']['BOOSTS'] else off}\n\n"
        f"**14.** Автореакции и Автоветки - {on if data['GENERAL']['REACTIONS_THREADS'] else off}\n\n"
        f"**15.** Автороли - {on if data['GENERAL']['ROLES'] else off}\n\n"
        f"**16.** Авто добавление очков за присутствие на событии - {on if data['GENERAL']['EVENT_REWARDING'] else off}\n\n",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    return embed


def create_welcome_embed():
    embed = {
        "title": "Приветствие 👋",
        "description": "Бот приветствует каждого нового участника в отдельном канале",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте заложено базовое сообщение, поэтому можешь просто выбрать, в какой канал будут отправляться оповещения",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Нажми на кнопку `Настроить` и измени поля, как тебе нужно (или оставь базовые)! Все поля сделаны под Embed\n\n"
                "Ты также можешь использовать переменные: `{member.mention}`, `{member.nick}`, `{member.name}`, `{member}` (вводи с фигурными скобками) ⚙️",
            },
        ],
    }
    return embed


def create_farewell_embed():
    embed = {
        "title": "Прощание 💀",
        "description": "Бот уведомляет об уходе участника в отдельном канале",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте заложено базовое сообщение, поэтому можешь просто выбрать, в какой канал будут отправляться оповещения",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Нажми на кнопку `Настроить` и измени сообщение, как тебе нужно (или оставь базовое (удобно))!\n\n"
                "Ты также можешь использовать переменные: `{member.mention}`, `{member.nick}`, `{member.name}`, `{member}` (вводи с фигурными скобками) ⚙️",
            },
        ],
    }
    return embed


def create_autoupdate_embed():
    embed = {
        "title": "Таблицы лидеров с автоматическим обновлением 📊",
        "description": "Бот отправляет сообщения с таблицами лидеров по очкам и количеству сообщений за последнюю неделю и автоматически обновляет их примерно раз в минуту",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте заложены базовые сообщения, поэтому можешь просто выбрать, в каком канале будут отправлены сообщения (желательно выбирать канал, где других сообщений не будет)",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Выбери тип таблицы, которую хочешь настроить, включить или выключить ⚙️",
            },
        ],
    }
    return embed


def create_autoupdate_scores_embed():
    embed = {
        "title": "Таблица лидеров по очкам за месяц 🏷️",
        "description": "Бот отправляет и автоматически обновляет сообщение с таблицей лидеров по очкам примерно раз в минуту",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте уже заложено базовое сообщение, поэтому можешь просто включить или выключить функцию",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Нажми на кнопку `Настроить` и измени поле `Лимит таблицы` так, как тебе нужно (от 0 до 20)",
            },
        ],
    }
    return embed


def create_autoupdate_messages_embed():
    embed = {
        "title": "Таблица лидеров по сообщениям за неделю 🏷️",
        "description": "Бот отправляет и автоматически обновляет сообщение с таблицей лидеров по сообщениям примерно раз в минуту",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте уже заложено базовое сообщение, поэтому можешь просто включить или выключить функцию",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Нажми на кнопку `Настроить` и измени поле `Лимит таблицы` так, как тебе нужно (от 0 до 20)",
            },
        ],
    }
    return embed


def create_scores_embed():
    embed = {
        "title": "Система очков ⚖️",
        "description": "Система очков - оценка участников путём присваивания им очков за любую активность (участие в ивентах, играх и т.п.)",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Нажми `Вкл` / `Выкл`, если хочешь / не хочешь использовать систему очков на своём сервере\n"
                "Функция включает в себя команды `/add, /remove, /set` с соответствующими подкомандами, а также `/топ, /реп, /reset` ⚙️",
            },
        ],
    }
    return embed


def create_experience_embed():
    embed = {
        "title": "Система опыта ⌛",
        "description": "Система опыта - поуровневая оценка активности участников на сервере путём присваивания им очков опыта за сообщения (для получения опыта необходимо написать хотя бы одно сообщения за последнюю минуту)",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Нажми `Вкл` / `Выкл`, если хочешь / не хочешь использовать систему опыта на своём сервере\n"
                "Функция включает в себя команды `/add, /remove, /set` с соответствующими подкомандами ⚙️",
            },
        ],
    }
    return embed


def create_feedback_embed():
    embed = {
        "title": "Система запросов к администрации 📟",
        "description": "Бот принимает запросы участников (по любой теме с её указанием), отправляет в отдельный канал "
        "с выбором кнопок: ответить (бот отправляет ответ в лс запросившему) или отклонить запрос; включена система напоминания о неотвеченных запросах",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте заложены базовые сообщения, поэтому можешь просто выбрать, в каком канале будет сообщение "
                "с кнопкой создания запросов, куда они будут отправляться и где будут напоминания",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Нажми на кнопку `Настроить` и измени поля сообщения, к которому будет прикреплена кнопка создания запроса, "
                "как тебе нужно (или оставь базовое)! Все поля сделаны под Embed",
            },
        ],
    }
    return embed


def create_scores_exp_embed():
    embed = {
        "title": "Система очков и Система опыта (уровни) 📀",
        "description": "Система очков - оценка участников путём присваивания им очков за любую активность (участие в ивентах, играх и т.п.)\n"
        "Система опыта - поуровневая оценка активности участников на сервере путём присваивания им очков опыта за сообщения",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Нажми `Вкл` / `Выкл`, если хочешь / не хочешь использовать систему очков и систему опыта на своём сервере",
            },
        ],
    }

    return embed


def create_games_embed():
    embed = {
        "title": "Игры 🎰",
        "description": "Бот предлагает азартные игры с возможностью поставить очки (система очков)",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Нажми `Вкл` / `Выкл`, чтобы сделать доступными / недоступными все игры",
            },
            {
                "name": "Кастомная настройка 🔖",
                "value": "Ты можешь выбрать каналы, в которых будут доступны игры, либо настроить каждую игру отдельно",
            },
        ],
    }

    return embed


def create_blackjack_embed():
    embed = {
        "title": "BlackJack ♠️",
        "description": "BlackJack - одна из самых популярных карточных игр в казино по всему миру. "
        "Цель - набрать как можно больше количество очков, но не больше 21-го, и обыграть бота.",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Нажми `Вкл` / `Выкл`, чтобы сделать доступной / недоступной игру",
            },
        ],
    }

    return embed


def create_roulette_embed():
    embed = {
        "title": "Roulette 🎲",
        "description": "Рулетка - стандартная азартная игра с случайной вероятностью выиграть очки",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Нажми `Вкл` / `Выкл`, чтобы сделать доступной / недоступной игру",
            },
        ],
    }

    return embed


def create_nearest_event_embed():
    embed = {
        "title": "Доска ближайших событий 📢",
        "description": "Бот отправляет сообщение с созданными событиями на сервере с разделением на категории и авто обновлением",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте нет заложенных категорий (будет использоваться категория `Другие`), "
                "но ты можешь добавить их позже и просто выбрать канал, куда отправлять сообщение",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "Нажми на кнопку `Настроить` и впиши категории для своих событий "
                "(чтобы бот мог сортировать ивенты, нужно либо в название, либо в описание события добавить название категории)",
            },
        ],
    }

    return embed


def create_moderation_embed():
    embed = {
        "title": "Модерация ⚔️",
        "description": "1. Защита от спама gif",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте заложены базовые сообщения, поэтому можешь просто нажать `Вкл` / `Выкл`",
            },
            {
                "name": "Кастомная настройка 🔖",
                "value": "Ты можешь выбрать каналы, в которых будет активна модерация",
            },
        ],
    }

    return embed


def create_roles_embed():
    embed = {
        "title": "ROLES",
        "description": "тут надо чёт написать",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "тут надо чёт написать",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "тут надо чёт написать",
            },
        ],
    }
    return embed


def create_roles_option_embed():
    embed = {
        "title": "ROLES_OPTION",
        "description": "тут надо чёт написать",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "тут надо чёт написать",
            },
            {
                "name": "Кастомные настройки 🔖",
                "value": "тут надо чёт написать",
            },
        ],
    }
    return embed


def create_reactions_threads_embed():
    embed = {
        "title": "Автореакции и Автоветки ♾️",
        "description": "Бот автоматически добавляет реакции и создает ветки к каждому сообщению в определённых каналах",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "В боте нет заложенных настроек. Нажми на `+`, чтобы добавить канал, "
                "в котором к каждому сообщению бот будет добавлять реакции или создавать ветки",
            },
        ],
    }

    return embed


def create_option_embed(option_channel=None):
    embed = {
        "title": "Автореакции и Автоветки",
        "description": "Бот автоматически добавляет реакции и создает ветки к каждому сообщению в определённых каналах",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "name": "Базовые настройки 💼",
                "value": "Выбери канал и нажми на `Настроить`, где нужно вписать код реакций через пробел, например: `<:B_chad:1172261856895840406> 🙂`. "
                "Если нужно, чтобы создавались ветки к каждому сообщению, нажми `Вкл`, либо `Выкл` для обратного",
            },
        ],
    }

    if option_channel:
        channel = {"name": "Канал", "value": option_channel}
        embed["fields"].append(channel)

    return embed


async def create_all_sets_embed(data, interaction):
    COGS = data["COGS"]
    embed = {
        "title": "Статус функций",
        "description": "Здесь отображаются все настройки и их статус",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "fields": [
            {
                "name": "Приветствие",
                "value": f"Статус: {'включено' if data['GENERAL']['WELCOME'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, COGS['WELCOME']['CHANNEL'])}\n"
                f"Заголовок: {COGS['WELCOME']['EMBED']['TITLE']}\n"
                f"Сообщение: {COGS['WELCOME']['EMBED']['DESCRIPTION']}\n"
                f"Цвет: {hex(COGS['WELCOME']['EMBED']['COLOR'])}\n"
                f"Автар для пользователей без него: {COGS['WELCOME']['EMBED']['AVATAR_IF_ERROR']}\n"
                f"Картинка: {COGS['WELCOME']['EMBED']['IMAGE']}\n",
            },
            {
                "name": "Прощание",
                "value": f"Статус: {'включено' if data['GENERAL']['FAREWELL'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, data['COGS']['FAREWELL']['CHANNEL'])}\n"
                f"Сообщение: {data['COGS']['FAREWELL']['MESSAGE']}\n",
            },
            {
                "name": "Обратная связь",
                "value": f"Статус: {'включено' if data['GENERAL']['REQUESTS'] else 'выключено'}\n"
                f"Канал (в котором обрабатываем обращения): {await get_channel_by_id(interaction, COGS['REQUESTS']['CHANNELS']['LOGS'])}\n"
                f"Канал (напоминания): {await get_channel_by_id(interaction, COGS['REQUESTS']['CHANNELS']['REMINDER'])}\n"
                f"Заголовок: {COGS['REQUESTS']['MESSAGE']['EMBED']['TITLE']}\n"
                f"Сообщение: {COGS['REQUESTS']['MESSAGE']['EMBED']['DESCRIPTION']}\n"
                f"Сообщение при взаимодействии: {COGS['REQUESTS']['MESSAGE']['CALLBACK']}\n"
                f"Цвет: {hex(COGS['REQUESTS']['MESSAGE']['EMBED']['COLOR'])}\n",
            },
            {
                "name": "Очки и опыт",
                "value": f"Статус: "
                f"{'включено' if data['GENERAL']['EXPERIENCE'] and data['GENERAL']['SCORES'] else 'выключено'}\n",
            },
            {
                "name": "Игры",
                "value": f"Все игры: {'включено' if data['GENERAL']['GAMES']['ALL_GAMES'] else 'выключено'}\n"
                f"Блэкджек: {'включено' if data['GENERAL']['GAMES']['BLACKJACK'] else 'выключено'}\n"
                f"Рулетка: {'включено' if data['GENERAL']['GAMES']['ROULETTE'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, COGS['GAMES']['CHANNELS'])}\n",
            },
            {
                "name": "Ближайшие события",
                "value": f"Статус: {'включено' if data['GENERAL']['NEAREST_EVENTS'] else 'выключено'}\n"
                f"Канал: {await get_channel_by_id(interaction, COGS['NEAREST_EVENTS']['CHANNEL'])}\n"
                f"Категории: {', '.join(COGS['NEAREST_EVENTS']['CATEGORIES'])}",
            },
            {
                "name": "Модерация",
                "value": f"Статус: {'включено' if data['GENERAL']['MODERATION']['GIF'] else 'выключено'}\n"
                f"Каналы: {await get_channel_by_id(interaction, COGS['MODERATION']['CHANNELS'])}\n"
                f"Сообщений до GIF: {COGS['MODERATION']['GIF']['DELAY']}",
            },
        ],
    }

    if len(COGS["REACTIONS_THREADS"].keys()) != 0:
        REACTIONS_THREADS = {"name": "Автореакции и автоветки"}
        channels_name = await get_channel_by_id(
            interaction, [*data["COGS"]["REACTIONS_THREADS"].keys()]
        )
        channels_name = channels_name.split() if isinstance(channels_name, str) else channels_name
        channels_id = [*data["COGS"]["REACTIONS_THREADS"].keys()]
        for i in range(len(channels_id)):
            REACTIONS_THREADS["value"] = (
                REACTIONS_THREADS.get("value", "") + channels_name[i] + ": " + "включено"
                if data["COGS"]["REACTIONS_THREADS"][channels_id[i]]["THREAD"]
                else "выключено"
            )

        embed["fields"].append(REACTIONS_THREADS)

    return embed


class GuildsManage(commands.Cog):
    """
    This class will manage bot (client) guilds, configure them
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.gdb = GuildsDBase()
        self.parent = {}
        self.keys = {
            "1": "WELCOME",
            "2": "FAREWELL",
            "3": ["MODERATION", "GIF"],
            "4": ["AUTOUPDATE", "MESSAGES"],
            "5": ["AUTOUPDATE", "SCORES"],
            "6": "NEAREST_EVENTS",
            "7": "EXPERIENCE",
            "8": ["GAMES", "BLACKJACK"],
            "9": ["GAMES", "ROULETTE"],
            "10": "ORDERS",
            "11": "REQUESTS",
            "12": "SCORES",
            "13": "BOOSTS",
            "14": "REACTIONS_THREADS",
            "15": "ROLES",
            "16": "EVENT_REWARDING",
        }

    @settings.sub_command(
        name="бота",
        description="Изменить настройки бота на сервере (обязательно)",
    )
    async def set_guild_settings(self, interaction: disnake.ApplicationCommandInteraction):
        if not await is_admin(interaction):
            return

        db = GuildsDBase()
        enc = JsonEncoder()
        default_config = enc.get_default_cfg()
        default_config["GUILD_ID"] = interaction.guild.id
        data = {
            "guild_id": interaction.guild.id,
            "guild_name": interaction.guild.name,
            "count_members": interaction.guild.member_count,
            "guild_sets": enc.code_to_json(default_config),
        }
        guild = await db.add_guild(data)
        if guild:
            set_view = GuildSettings(interaction, enc.code_from_json(guild.guild_sets))
            self.parent[str(interaction.guild.id)] = set_view
            await interaction.send(".")
            await set_view.create_home_view()
        else:
            await interaction.response.send_message("Что-то пошло не так :(")

    @settings.sub_command(
        name="текущая",
        description="Показать текущие настройки бота на сервере",
    )
    async def current_settings(self, interaction: disnake.ApplicationCommandInteraction):
        if not await is_admin(interaction):
            return

        gdb: GuildsDBase = GuildsDBase()
        guild: Guilds = await gdb.get_guild(guild_id=interaction.guild.id)
        enc: JsonEncoder = JsonEncoder()
        if guild:
            await interaction.response.send_message(
                embed=disnake.Embed.from_dict(
                    await create_all_sets_embed(enc.code_from_json(guild.guild_sets), interaction)
                ),
                ephemeral=True,
            )

    @update.sub_command_group()
    async def gdb(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @gdb.sub_command()
    async def add(self, interaction: disnake.ApplicationCommandInteraction):
        if not is_admin(interaction):
            return

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

    @gdb.sub_command()
    async def default_sets(self, interaction: disnake.ApplicationCommandInteraction):
        if not is_admin(interaction):
            return

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

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.type == disnake.InteractionType.component:
            if interaction.component.custom_id == "home_screen":
                if not await is_admin(interaction):
                    return

                value = interaction.values[0]
                if value == "greetings":
                    await stud_interaction(interaction)
                    await GuildSettings.create_welcome_view(self.parent[str(interaction.guild.id)])

                elif value == "farewell":
                    await stud_interaction(interaction)
                    await GuildSettings.create_farewell_view(self.parent[str(interaction.guild.id)])

                elif value == "autoupdate":
                    await stud_interaction(interaction)
                    await GuildSettings.create_autoupdate_view(
                        self.parent[str(interaction.guild.id)]
                    )

                elif value == "feedback":
                    await stud_interaction(interaction)
                    await GuildSettings.create_feedback_view(self.parent[str(interaction.guild.id)])

                elif value == "scores":
                    await stud_interaction(interaction)
                    await GuildSettings.create_scores_view(self.parent[str(interaction.guild.id)])

                elif value == "experience":
                    await stud_interaction(interaction)
                    await GuildSettings.create_exp_view(self.parent[str(interaction.guild.id)])

                elif value == "games":
                    await stud_interaction(interaction)
                    await GuildSettings.create_games_view(self.parent[str(interaction.guild.id)])

                elif value == "nearest_events":
                    await stud_interaction(interaction)
                    await GuildSettings.create_nearest_events_view(
                        self.parent[str(interaction.guild.id)]
                    )

                elif value == "moderation":
                    await stud_interaction(interaction)
                    await GuildSettings.create_moderation_view(
                        self.parent[str(interaction.guild.id)]
                    )

                elif value == "adding_reactions_threads":
                    await stud_interaction(interaction)
                    await GuildSettings.create_auto_reactions_threads_view(
                        self.parent[str(interaction.guild.id)]
                    )

                elif value == "roles":
                    await stud_interaction(interaction)
                    await GuildSettings.create_autoroles_view(
                        self.parent[str(interaction.guild.id)]
                    )

            if "fn_" in interaction.component.custom_id:
                if not await is_admin(interaction):
                    return

                await toggle_set_easy(self, interaction)

            if "back" in interaction.component.custom_id:
                await GuildSettings.create_home_view(self.parent[str(interaction.guild.id)])


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
