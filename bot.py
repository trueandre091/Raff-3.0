from DB.JSONEnc import JsonEncoder
import config as cfg
from cogs.counter_functions import *
from cogs.on_message_functions import *
from cogs.cog_experience import count_experience
from DB.DataBase import GuildsDbase

GDB = GuildsDbase()
encoder = JsonEncoder()

bot = commands.Bot(
    command_prefix="none",
    help_command=None,
    intents=disnake.Intents.all(),
    chunk_guilds_at_startup=False,
)
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


async def guild_sets_check(
    guild_id: int, checking_set_1: str = None, checking_set_2: str = None, checking_set_3: str = None
) -> dict:
    """Checking if guild exists in DB or if certain functions are turned on guild"""
    guild = await GDB.get_guild(guild_id)
    if guild:
        guild = encoder.code_from_json(guild.guild_sets)
        if checking_set_1 and checking_set_2 and checking_set_3:
            if guild[checking_set_1][checking_set_2][checking_set_3]:
                return guild[checking_set_1]
        elif checking_set_1 and checking_set_2:
            if guild[checking_set_1][checking_set_2]:
                return guild[checking_set_1]
        elif checking_set_1:
            if guild[checking_set_1]:
                return guild[checking_set_1]
        else:
            return guild


@bot.event
async def on_member_join(member: disnake.Member):
    """Greeting newbies when they come"""
    settings = await guild_sets_check(member.guild.id, "WELCOME_SETTINGS", "CHANNEL")
    if settings is None:
        return

    channel = bot.get_channel(settings["CHANNEL"])
    variables = {
        "member.mention": member.mention,
        "member.name": member.name,
        "member.nick": member.nick,
        "member": member,
    }
    embed_dict = {
        "title": settings["EMBED"]["TITLE"].format(**variables),
        "description": settings["EMBED"]["DESCRIPTION"].format(**variables),
        "image": {"url": settings["BACKGROUND_IMAGE"]},
        "thumbnail": {},
        "color": settings["EMBED"]["COLOR"],
        "timestamp": str(datetime.now()),
    }
    try:
        embed_dict["thumbnail"]["url"] = member.avatar.url
    except AttributeError:
        embed_dict["thumbnail"]["url"] = settings["AVATAR_IF_ERROR"]

    await channel.send(embed=disnake.Embed.from_dict(embed_dict))


@bot.event
async def on_member_remove(member):
    """Farewell to members when they leave"""
    settings = await guild_sets_check(member.guild.id, "FAREWELL_SETTINGS", "CHANNEL")
    if settings is None:
        return

    channel = bot.get_channel(settings["CHANNEL"])
    variables = {
        "member.mention": member.mention,
        "member.name": member.name,
        "member.nick": member.nick,
        "member": member,
    }

    await channel.send(settings["MESSAGE"].format(**variables))


@bot.event
async def on_message(message):
    """On every sent message functions"""
    settings = await guild_sets_check(message.guild.id)
    if settings is None:
        return

    await count_every_message(message)

    await count_experience(message, settings["COGS_SETTINGS"]["EXPERIENCE"])

    await moderation(message, settings["MODERATION_SETTINGS"])

    await reactions_thread_check(message, settings["ADDING_REACTIONS_THREADS_SETTINGS"])

    await boosts_check(message, settings["BOOSTS_COUNTING_SETTINGS"])

    await order_command_check(bot, message, settings["COGS_SETTINGS"]["ORDERS"])


@bot.event
async def on_ready():
    """Bot writes in console when it starts"""
    print(f"Bot {bot.user} is ready to work!")


bot.run(cfg.TOKEN)
