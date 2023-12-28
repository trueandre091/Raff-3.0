import config as cfg
from cogs.counter_functions import *
from cogs.on_message_functions import *
from cogs.guilds_functions import guild_sets_check, GDB
from cogs.cog_experience import count_experience

bot = commands.Bot(
    command_prefix="none",
    help_command=None,
    intents=disnake.Intents.all(),
    chunk_guilds_at_startup=False,
)
# bot.load_extension("cogs.cog_autoupdate")
# bot.load_extension("cogs.cog_counters")
bot.load_extension("cogs.cog_events")
bot.load_extension("cogs.cog_games")
bot.load_extension("cogs.cog_orders")
bot.load_extension("cogs.cog_requests")
# bot.load_extension("cogs.cog_scores")
# bot.load_extension("cogs.cog_special")
bot.load_extension("cogs.cog_experience")


bot.load_extension("cogs.cog_setguilds")


@bot.event
async def on_member_join(member: disnake.Member):
    """Greeting newbies when they come"""
    settings = await guild_sets_check(member.guild.id, "GENERAL_SETTINGS", "WELCOME")
    if settings is None:
        return
    settings = settings["WELCOME_SETTINGS"]

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
    settings = await guild_sets_check(member.guild.id, "GENERAL_SETTINGS", "FAREWELL")
    if settings is None:
        return
    settings = settings["FAREWELL_SETTINGS"]

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
    guild = await guild_sets_check(message.guild.id)
    if guild is None:
        return

    await count_every_message(message)

    await count_experience(message, guild)

    await moderation(message, guild)

    await reactions_thread_check(message, guild)

    await boosts_check(message, guild)

    await order_command_check(bot, message, guild)


@bot.event
async def on_guild_join(guild: disnake.Guild):
    gdb = GuildsDBase()
    data = {"guild_id": guild.id, "guild_name": guild.name, "count_members": guild.member_count}

    for _ in range(5):
        res = await gdb.add_guild(data)
        if res:
            break


dicts = {
    "TOKEN": "",
    "GUILD_ID": 785312593614209055,
    "GENERAL_SETTINGS": {
        "PASSWORD": 152364,
        "WELCOME": False,
        "FAREWELL": False,
        "MODERATION": {"GIF": False},
        "AUTOUPDATE_MESSAGES": {"MESSAGES": True, "SCORES": True},
        "NEAREST_EVENTS": True,
        "EXPERIENCE": False,
        "GAMES": {"BLACKJACK": True, "ROULETTE": False},
        "ORDERS": True,
        "REQUESTS": True,
        "SCORES": False,
        "COUNTING_BOOSTS": False,
        "ADDING_REACTIONS_THREADS": True,
    },
    "TIMERS": {
        "CHANNEL": 785312596546813974,
        "MESSAGE": "По любым вопросам --> <#992788044514082876> <:B_andre2:1053723610197524530>",
    },
    "WELCOME_SETTINGS": {
        "CHANNEL": 785312596059226114,
        "EMBED": {
            # возможно использование переменных: {member.mention}, {member}
            "TITLE": "Добро пожаловать на Homey Temple!  💌",
            # возможно использование переменных: {member.mention}, {member}
            "DESCRIPTION": "{member.mention}, приветствуею тебя на сервере!\nПриходи на ближайшие мероприятия, если будет время <#1160687361269694505> 🌼",
            "COLOR": 0x2B2D31,
        },
        "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
        "BACKGROUND_IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
    },
    "FAREWELL_SETTINGS": {
        "CHANNEL": 785313517481099274,
        # возможно использование переменных: {member.mention}, {member.nick}, {member.name}, {member}
        "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл.",
    },
    "ADDING_REACTIONS_THREADS_SETTINGS": {
        "858731672677515294": {"REACTIONS": [], "THREAD": True},
        "785312596546813976": {
            "REACTIONS": ["<:B_00like:1001544330613375026>", "<:B_00likenot:1001544295532204082>"],
            "THREAD": True,
        },
        "1160687361269694505": {
            "REACTIONS": ["<:B_00like:1001544330613375026>", "<:B_00likenot:1001544295532204082>", "✅"],
            "THREAD": False,
        },
    },
    "MODERATION_SETTINGS": {"GIF": {"MESSAGES_FOR_GIF": 15}},
    "BOOSTS_COUNTING_SETTINGS": {
        "BOOST_BOTS": {"DSMonitoring": 575776004233232386, "SD.C Monitoring": 464272403766444044},
        "REMINDER": 478321260481478677,
    },
    "COGS_SETTINGS": {
        "SPECIAL": {
            "ROLES": {
                "BOOSTS": {
                    "ROLES_HAVE": [
                        1056169412585066536,
                        1028040256903188530,
                        1056169408487247952,
                        1056169387872227370,
                        1071772832599650324,
                        785875027085492245,
                    ],
                    "ROLES_GET": [1056171848552939581],
                }
            },
            "EVENTS": {
                "TIME": 1860,
                "CHANNELS": [858737175439736873, 1186721973242429480, 1046504818249846845, 1010586706677866626],
                "SCORES": 1,
            },
        },
        "SCORES": {"AMOUNT_TO_FIRST_LVL": 8, "AMOUNT_TO_THIRD_LVL": 12, "AMOUNT_TO_FIFTH_LVL": 20},
        "GAMES": {"ROULETTE": {"CHANCE": 60}, "BLACKJACK": True},
        "AUTOUPDATE": {
            "MESSAGES": {"PLACE_LIMIT": 10, "PREVIOUS_BESTS_LIMIT": 3},
            "SCORES": {},
            "CHANNEL": 994881716307116073,
        },
        "EVENTS": {"CHANNEL": 1160687361269694505, "CATEGORIES": ["Еженедельный"]},
        "ORDERS": {"CHANNEL": 829075875013591101, "BARMEN_ROLE": 829082636705595433},
        "REQUESTS": {
            "BUTTONS_MESSAGE": {
                "CHANNEL": 992788044514082876,
                "EMBED": {
                    "TITLE": "Служба поддержки 📟",
                    "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации и оставить отзыв о качестве поддержки, нажав на соответствующие кнопки ниже",
                    "COLOR": 0x2B2D31,
                },
                "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\n`Ждите ответ от администрации, он будет отправлен вам в личные сообщения`",
            },
            "LOGS_MESSAGE": {"CHANNEL": 981593893567070298},
            "ADMIN_CHANNEL": 981593763988275210,
        },
        "EXPERIENCE": {"FACTOR": 5, "LEVELING": [{"ROLE": None, "AMOUNT": None}]},
    },
}


@bot.event
async def on_ready():
    """Bot writes in console when it starts"""
    print(f"Bot {bot.user} is ready to work!")
    await GDB.update_guild({"guild_id": 785312593614209055, "guild_sets": dicts})


bot.run(cfg.TOKEN)
