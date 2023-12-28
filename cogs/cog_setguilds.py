import disnake
from disnake.ext import commands
from disnake.ui import View, button, select, Button, Modal
from disnake.ui import Select, channel_select
from disnake import SelectOption, ModalInteraction
import datetime
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder


class GuildSettings:
    def __init__(self, interaction: disnake.Interaction, settings):
        self.interaction = interaction
        self.gdb = GuildsDBase()
        self.settings = settings

    async def create_home_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_hello_embed()), view=GuildSetsHomeScreenView()
        )

    async def create_welcome_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_welcome_cfg()), view=GuildSetsGreetView()
        )

    async def create_farewell_view(self):
        await self.interaction.edit_original_response(
            embed=disnake.Embed.from_dict(create_farewell_cfg()), view=GuildSetsGreetView()
        )


class GuildSetsHomeScreenView(View):
    def __init__(self):
        super().__init__(timeout=3600)

    @select(
        custom_id="home_screen",
        min_values=1,
        max_values=1,
        placeholder="Что хочешь настроить?",
        options=[
            SelectOption(
                label="Приветствие", description="Настрой собственное приветствие", emoji="🙋‍♂️", value="greetings"
            ),
            SelectOption(label="Прощание", description="Настрой собственное прощание", emoji="👋", value="farewell"),
            SelectOption(
                label="Обратная связь",
                description="Получи отзывы и предложения для своего сервера",
                emoji="🤙",
                value="feedback",
            ),
            SelectOption(
                label="Очки и опыт", description="Попробуй нашу систему очков и опыта", emoji="🪙", value="scores_exp"
            ),
            SelectOption(label="Игры", description="Настрой игры как пожелаешь", emoji="🎮", value="games"),
        ],
    )
    async def select_set_callback(self, selectMenu: Select, interaction: disnake.Interaction):
        value = selectMenu.values
        if value == "greetings":
            pass


class GuildSetsGreetView(View):
    @channel_select(
        channel_types=[disnake.ChannelType.text, disnake.ChannelType.news],
        placeholder="В каком канале приветствовать?",
        min_values=0,
    )
    async def callback(self, selectMenu: Select, interaction: disnake.Interaction):
        pass

    @button(label="Назад")
    async def to_back_callback(self, button: Button, interaction: disnake.Interaction):
        await GuildSettings.create_home_view()

    @button(label="Настроить")
    async def open_greet_set_callback(self, button: Button, interaction: disnake.Interaction):
        await interaction.response.send_modal(GreetModal())


class GreetModal(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, title="Настройка приветствий")

        self.add_text_input(
            label="Заголовок",
            placeholder="Добро пожаловать на сервер!  💌",
            min_length=4,
            max_length=75,
            required=True,
            custom_id="title",
        )
        self.add_text_input(
            label="Сообщение",
            placeholder="{member.mention}, рады тебя видеть!"
            "Приходи на ближайшие мероприятия, если будет время <#1160687361269694505> 🌼",
            style=disnake.TextInputStyle.paragraph,
            max_length=256,
            required=False,
            custom_id="description",
        )
        self.add_text_input(
            label="Аватарка (дефолтная)",
            placeholder="Вставь ссылку из интернета",
            required=False,
            custom_id="url_to_ava",
        )
        self.add_text_input(
            label="Твоя картинка",
            placeholder="Вставь ссылку из интернета",
            required=False,
            custom_id="background_image",
        )

    async def callback(self, interaction: ModalInteraction):
        title = interaction.text_values["title"]
        description = interaction.text_values["description"]
        url_to_ava = interaction.text_values["url_to_ava"]
        background_image = interaction.text_values["background_image"]

        gdb = GuildsDBase()
        enc = JsonEncoder()

        guild = await gdb.get_guild({"guild_id": interaction.guild.id})
        if guild:
            settings = enc.code_from_json(guild.guild_sets)
            settings["WELCOME_SETTINGS"]["EMBED"]["TITLE"] = title
            settings["WELCOME_SETTINGS"]["EMBED"]["DESCRIPTION"] = description
            settings["WELCOME_SETTINGS"]["AVATAR_IF_ERROR"] = url_to_ava
            settings["WELCOME_SETTINGS"]["BACKGROUND_IMAGE"] = background_image

            await gdb.update_guild({"guild_id": guild.guild_id, "guild_sets": settings})


class GuildSetsFarewellView(View):
    pass


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
            {"name": "Базовые настройки", "value": "Не забудь выбрать канал для прощаний"},
            {
                "name": "Кастомное прощание",
                "value": "Ты можешь использовать упоминания как и в приветствиях. На выбор: {member.mention}, {member.nick}, {member.name}, {member}.\n"
                "Ты точно сможешь найти что-то подходящее",
            },
        ],
    }


class GuildsManage(commands.Cog):
    """
    This class will manage bot (client) guilds, configure them
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="настройка_бота", description="Поменять настройки сервера")
    @commands.has_permissions(administrator=True)
    async def set_guild_settings(self, interaction: disnake.ApplicationCommandInteraction):
        db = GuildsDBase()
        data = {
            "guild_id": interaction.guild.id,
            "guild_name": interaction.guild.name,
            "count_members": interaction.guild.member_count,
        }
        guild_sets = await db.add_guild(data)
        if guild_sets:
            set_view = GuildSettings(interaction, guild_sets.guild_sets)
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


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
