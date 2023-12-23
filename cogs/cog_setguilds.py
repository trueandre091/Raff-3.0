import disnake
from disnake.ext import commands
import datetime
from DB.DataBase import GuildsDbase


def create_hello_embed():
    embed = {
        "title": "Привет",
        "description": "",
        "color": 0x2B2D31,
        "timestamp": datetime.datetime.now().isoformat(),
        "author": None,
        "fields": [
            {
                "value": "Прежде чем начать пользоваться этим ботом и использовать весь функионал его необходимо настроить. "
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
                "value": "Чтобы бот начал приветствовать новых участников необходимо выбрать канал"
            },
            {
                "name": "Кастомное приветствие",
                "value": "Просто нажмина кнопку 'Настроить', введи заголовок, текст своего приветствия и используй! \n"
                "Ты так же можешь упомянуть пользователя, который только что зашёл на сервер. Для этого напиши {member.mention} или {member} на то место, где его требуется упомянуть. \n",
            },
            {
                "name": "Кастомные картинки",
                "value": "Иногда аватарка пользователья может не загрузится или просто отсутствовать. Для таких случае ты можешь выбрать аватар, который будет показываться вместо пользовательского. Просто вставь ссылку из интернета на картинку! \n"
                "Хочешь чтобы твоё приветствие было особенным? Тогда используй свой фон для приветствий!"
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
                "value": "Не забудь выбрать канал для прощаний"
            },
            {
                "name": "Кастомное прощание",
                "value": "Ты можешь использовать упомянания как и в приветствиях. На выбор: {member.mention}, {member.nick}, {member.name}, {member}.\n"
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

    @commands.slash_command(name="Настройка бота", description="Поменять настройки сервера")
    @commands.has_permissions(administrator=True)
    async def set_guild_settings(self, interaction: disnake.Interaction):
        db = GuildsDbase()
        data = {
            "guild_id": interaction.guild.id,
            "guild_name": interaction.guild.name,
            "count_members": interaction.guild.member_count,
        }
        guild_sets = await db.add_guild(data)
        if guild_sets:
            embed_dict = create_hello_embed()
            await interaction.response.send_message(embed=disnake.Embed.from_dict(embed_dict))


def setup(bot: commands.Bot):
    bot.add_cog(GuildsManage(bot))
