import config as cfg
from cogs.counter_functions import *
from cogs.on_message_functions import *

bot = commands.Bot(
    command_prefix="none", help_command=None, intents=disnake.Intents.all(), chunk_guilds_at_startup=False
)

# bot.load_extensions("cogs")


@bot.event
async def on_member_join(member):
    """Greeting newbies when they come"""
    settings = cfg.WELCOME_SETTINGS
    channel = bot.get_channel(settings["CHANNEL"])
    member = member.mention
    embed_dict = {
        "title": settings["TITLE"],
        "description": member + settings["EMBED"]["DESCRIPTION"],
        "image": {"url": settings["BACKGROUND_IMAGE"]},
        "color": settings["EMBED"]["COLOR"],
        "timestamp": datetime.now()
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

    await channel.send(f"{member.mention} / {member.name} / {member.nick} ушёл.")


@bot.event
async def on_message(message):
    """On every sent message functions"""

    await count_every_message(message)

    await reactions_thread_check(message, cfg.ADDING_REACTIONS_THREADS_SETTINGS)

    await boosts_check(message, cfg.BOOSTS_COUNTING_SETTINGS)

    await order_command_check(bot, message, cfg.ORDERS_SETTINGS)

    await moderation(message, cfg.MODERATION_SETTINGS)


@bot.event
async def on_ready():
    """Bot writes in console when it starts"""
    print(f"Bot {bot.user} is ready to work!")


bot.run(cfg.TOKEN)
