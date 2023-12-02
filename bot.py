from datetime import datetime
import disnake
from disnake.ext import commands
from json import load, dump

bot = commands.Bot(command_prefix="none", help_command=None, intents=disnake.Intents.all(),
                   test_guilds=[785312593614209055], chunk_guilds_at_startup=False)

bot.load_extension("cogs.cog_scores")
bot.load_extension("cogs.cog_requests")
bot.load_extension("cogs.cog_events")
bot.load_extension("cogs.cog_games")
bot.load_extension("cogs.cog_orders")
bot.load_extension("cogs.cog_autoupdate")
bot.load_extension("cogs.cog_counters")

with (open("config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")


############################################################################################


@bot.event  # приветствие новичков
async def on_member_join(member):
    channel = bot.get_channel(CONFIG["CHANNEL_WELCOME"])
    description = (f"{member.mention} , рады тебя видеть!\nПриходи на ближайшие мероприятия, если будет время "
                   f"<#1160687361269694505> 🌼")

    url_1 = "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png"
    url_2 = ("https://images-ext-2.discordapp.net/external/0VobeQ2Ot6zcKqL3Qgj1EIN9B2xyrxbFGGQR444w3Os/https/im.wampi"
             ".ru/2023/03/02/DALLE-2023-02-22-19.01.33---a-spring-flowery-background.png")

    embed = disnake.Embed(
        title="Добро пожаловать на Homey Temple!  💌",
        description=description,
        color=0x2b2d31,
        timestamp=datetime.now()
    )

    try:
        embed.set_thumbnail(url=member.avatar.url)
    except AttributeError:
        embed.set_thumbnail(url=url_1)

    embed.set_image(url=url_2)

    await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(CONFIG["CHANNEL_BYE"])
    await channel.send(f"{member.mention} / {member.name} / {member.nick} ушёл.")


############################################################################################


async def add_orders_counter():
    with (open(f"data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["ORDERS"] += 1

    with (open(f"data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def add_failed_gif_counter():
    with (open(f"data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["FAILED_GIF_TRY"] += 1

    with (open(f"data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def add_number_of_events_counter():
    with (open(f"data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["NUMBER_OF_EVENTS"] += 1

    with (open(f"data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


############################################################################################


@bot.event  # автосоздание веток и реакций (лайк и дизлайк)
async def on_message(message):
    channels = [CONFIG[key] for key in ["CHANNEL_ANNOUNCE", "CHANNEL_SUGGEST"]]
    boost_bots = CONFIG["BOOST_BOTS"]

    author_id = message.author.id

    if not message.author.bot:
        with(open("data/lb_messages_data.json", 'r', encoding='utf-8') as f):
            data = load(f)

        if str(author_id) not in data:
            data[str(author_id)] = 1
        else:
            data[str(author_id)] += 1

        with(open("data/lb_messages_data.json", 'w', encoding='utf-8') as f):
            dump(data, f)

    ############################################################################################

    if message.channel.id in channels:
        like = "<:B_00like:1001544330613375026>"
        dislike = "<:B_00likenot:1001544295532204082>"

        await message.create_thread(name="Комментарии")

        if message.channel.id == CONFIG["CHANNEL_SUGGEST"]:
            await message.add_reaction(like)
            await message.add_reaction(dislike)

    elif message.type == disnake.MessageType.application_command and author_id in boost_bots:

        if author_id == boost_bots[1]:
            flag = True
            async for msg in message.channel.history(limit=50):
                if msg.type == disnake.MessageType.application_command and msg.interaction.name == "up":
                    flag = False
                if msg.author.id == 478321260481478677 and "/up" in msg.content:
                    break
            if flag:

                member_id = message.interaction.user.id

                with(open('data/counters.json', 'r', encoding='utf-8') as f):
                    data = load(f)

                if str(member_id) not in data["LIKERS"]:
                    data["LIKERS"][str(member_id)] = 1
                else:
                    data["LIKERS"][str(member_id)] += 1

                with(open('data/counters.json', 'w', encoding='utf-8') as f):
                    dump(data, f)

        if author_id == boost_bots[0]:
            if "Вы успешно лайкнули сервер." in message.embeds[-1].to_dict()["description"]:

                member_id = message.interaction.user.id

                with(open('data/counters.json', 'r', encoding='utf-8') as f):
                    data = load(f)

                if str(member_id) not in data["LIKERS"]:
                    data["LIKERS"][str(member_id)] = 1
                else:
                    data["LIKERS"][str(member_id)] += 1

                with(open('data/counters.json', 'w', encoding='utf-8') as f):
                    dump(data, f)

    elif message.channel.id == CONFIG["CHANNEL_EVENTS"]:
        tick = "✅"
        like = "<:B_00like:1001544330613375026>"
        dislike = "<:B_00likenot:1001544295532204082>"

        await message.add_reaction(tick)
        await message.add_reaction(like)
        await message.add_reaction(dislike)

    ############################################################################################

    elif '/заказ ' in message.content:

        channel = bot.get_channel(CONFIG["CHANNEL_RPBAR"])
        barmen_role = "<@&829082636705595433>"

        if message.channel.id != CONFIG["CHANNEL_RPBAR"]:

            await message.reply(
                f"Эта команда может быть использована только в канале {channel.mention}!",
                delete_after=5
            )

        else:

            await add_orders_counter()

            embed = disnake.Embed(
                title="Новый заказ 📥",
                description=f"{message.author.mention}\n{message.content.strip('/заказ ')}",
                color=0x2b2d31,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Тоже хочешь заказать что-нибудь? Пропиши /заказ через нашего бота!")

            await message.reply(
                f"Доброго времени суток {message.author.mention}! Бармен скоро подойдёт 🐥",
                delete_after=20.0
            )
            await channel.send(barmen_role, embed=embed)

    ############################################################################################

    elif message.attachments:
        if 'gif' in message.attachments[0].url:
            channel = message.channel

            flag = False
            c = False
            async for msg in channel.history(limit=CONFIG["SETTINGS"]["MESSAGES_FOR_GIF"] + 1):
                if c:
                    if msg.attachments:
                        if 'gif' in msg.attachments[0].url:
                            flag = True
                            break
                    if 'gif' in msg.content:
                        flag = True
                        break
                c = True

            if flag:
                await add_failed_gif_counter()

                await message.reply(f"*Гифки можно отправлять раз в {CONFIG['SETTINGS']['MESSAGES_FOR_GIF']} "
                                    f"сообщений* <a:A_heart1:993383076363239444>", delete_after=3)
                await message.delete()

    elif 'gif' in message.content:
        channel = message.channel

        flag = False
        c = False
        async for msg in channel.history(limit=CONFIG["SETTINGS"]["MESSAGES_FOR_GIF"] + 1):
            if c:
                if msg.attachments:
                    if 'gif' in msg.attachments[0].url:
                        flag = True
                        break
                if 'gif' in msg.content:
                    flag = True
                    break
            c = True

        if flag:
            await add_failed_gif_counter()

            await message.reply(f"*Гифки можно отправлять раз в {CONFIG['SETTINGS']['MESSAGES_FOR_GIF']} "
                                f"сообщений* <a:A_heart1:993383076363239444>", delete_after=3)
            await message.delete()


############################################################################################


bot.run(CONFIG["TOKEN"])
