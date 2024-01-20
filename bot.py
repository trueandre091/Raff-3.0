import disnake
import config as cfg
from cogs.on_message_functions import *
from cogs.cog_guilds_functions import guild_sets_check, GDB, dicts1, dicts
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder
from loguru import logger

logger.add(
    "logs/logs.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
    level="INFO",
    rotation="1 week",
    compression="zip",
    backtrace=True,
    diagnose=True,
)

bot = commands.Bot(
    command_prefix="none",
    help_command=None,
    intents=disnake.Intents.all(),
    chunk_guilds_at_startup=False,
)


@bot.slash_command(
    default_member_permissions=disnake.Permissions(administrator=True),
    description="Установить",
)
async def set(interaction: disnake.ApplicationCommandInteraction):
    pass


@bot.slash_command(
    default_member_permissions=disnake.Permissions(administrator=True),
    description="Прибавить",
)
async def add(interaction: disnake.ApplicationCommandInteraction):
    pass


@bot.slash_command(
    default_member_permissions=disnake.Permissions(administrator=True),
    description="Вычесть",
)
async def remove(interaction: disnake.ApplicationCommandInteraction):
    pass


@bot.slash_command(
    default_member_permissions=disnake.Permissions(administrator=True),
    description="Обновить",
)
async def update(interaction: disnake.ApplicationCommandInteraction):
    pass


bot.load_extension("cogs.cog_autoupdate")
bot.load_extension("cogs.cog_counters")
bot.load_extension("cogs.cog_events")
bot.load_extension("cogs.cog_games")
bot.load_extension("cogs.cog_orders")
bot.load_extension("cogs.cog_requests")
bot.load_extension("cogs.cog_scores")
bot.load_extension("cogs.cog_special")
bot.load_extension("cogs.cog_experience")
bot.load_extension("cogs.cog_setguilds")
bot.load_extension("cogs.cog_guilds_functions")


@bot.event
async def on_message(message: disnake.Message):
    """On every sent message functions"""
    settings = await guild_sets_check(message.guild.id)
    if settings is None:
        return

    await count_every_message(message)

    await count_experience(message, settings)

    await moderation(message, settings)

    await reactions_thread_check(message, settings)

    await boosts_check(message, settings)

    await order_command_check(bot, message, settings)


@bot.event
async def on_guild_join(guild: disnake.Guild):
    gdb: GuildsDBase = GuildsDBase()
    enc: JsonEncoder = JsonEncoder()
    default_cfg = enc.get_default_cfg()
    default_cfg["GUILD_ID"] = guild.id
    data = {
        "guild_id": guild.id,
        "guild_name": guild.name,
        "count_members": guild.member_count,
        "guild_sets": enc.code_to_json(default_cfg),
    }

    for _ in range(5):
        res = await gdb.add_guild(data)
        if res:
            break


@bot.event
async def on_ready():
    """Bot writes in console when it starts"""
    logger.info(f"Bot {bot.user} is ready to work!")
    # await GDB.update_guild(guild_id=785312593614209055, guild_sets=dicts)


bot.run(cfg.TOKEN)
