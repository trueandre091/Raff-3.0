import config as cfg
from cogs.counter_functions import *
from cogs.on_message_functions import *
from cogs.cog_experience import count_experience

bot = commands.Bot(
    command_prefix="none", help_command=None, intents=disnake.Intents.all(), chunk_guilds_at_startup=False
)
bot.load_extension("cogs.cog_autoupdate")
bot.load_extension("cogs.cog_counters")
bot.load_extension("cogs.cog_events")
bot.load_extension("cogs.cog_games")
bot.load_extension("cogs.cog_orders")
bot.load_extension("cogs.cog_requests")
bot.load_extension("cogs.cog_scores")
bot.load_extension("cogs.cog_special")


@bot.event
async def on_member_join(member):
    """Greeting newbies when they come"""
    settings = cfg.WELCOME_SETTINGS
    channel = bot.get_channel(settings["CHANNEL"])
    variables = {
        "member.mention": member.mention, "member.name": member.name, "member.nick": member.nick, "member": member
    }
    embed_dict = {
        "title": settings["EMBED"]["TITLE"].format(**variables),
        "description": settings["EMBED"]["DESCRIPTION"].format(**variables),
        "image": {"url": settings["BACKGROUND_IMAGE"]},
        "thumbnail": {},
        "color": settings["EMBED"]["COLOR"],
        "timestamp": str(datetime.now())
    }
    try:
        embed_dict["thumbnail"]["url"] = member.avatar.url
    except AttributeError:
        embed_dict["thumbnail"]["url"] = settings["AVATAR_IF_ERROR"]

    await channel.send(embed=disnake.Embed.from_dict(embed_dict))


@bot.event
async def on_member_remove(member):
    """Farewell to members when they leave"""
    settings = cfg.FAREWELL_SETTINGS
    channel = bot.get_channel(settings["CHANNEL"])
    variables = {
        "member.mention": member.mention, "member.name": member.name, "member.nick": member.nick, "member": member
    }

    await channel.send(settings["MESSAGE"].format(**variables))


@bot.event
async def on_message(message):
    """On every sent message functions"""

    await count_every_message(message)

    await count_experience(message)

    await moderation(message, cfg.MODERATION_SETTINGS)

    await reactions_thread_check(message, cfg.ADDING_REACTIONS_THREADS_SETTINGS)

    await boosts_check(message, cfg.BOOSTS_COUNTING_SETTINGS)

    await order_command_check(bot, message, cfg.COGS_SETTINGS["ORDERS"])


@bot.event
async def on_ready():
    """Bot writes in console when it starts"""
    print(f"Bot {bot.user} is ready to work!")


bot.run(cfg.TOKEN)
