import asyncio
from datetime import datetime
import disnake
from disnake.ext import commands
from json import load, dump

bot = commands.Bot(command_prefix=".", help_command=None, intents=disnake.Intents.all(),
                   test_guilds=[785312593614209055], chunk_guilds_at_startup=False)

bot.load_extension("cogs.cog_scores")
bot.load_extension("cogs.cog_requests")
bot.load_extension("cogs.cog_events")
bot.load_extension("cogs.cog_games")

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


@bot.event  # автосоздание веток и реакций (лайк и дизлайк)
async def on_message(message):
    channels = [CONFIG[key] for key in ["CHANNEL_ANNOUNCE", "CHANNEL_SUGGEST"]]

    like = "<:B_00like:1001544330613375026>"
    dislike = "<:B_00likenot:1001544295532204082>"
    tick = "✅"

    if message.channel.id in channels:

        await message.create_thread(name="Комментарии")

        if message.channel.id == CONFIG["CHANNEL_SUGGEST"]:

            await message.add_reaction(like)
            await message.add_reaction(dislike)

    elif message.author.id == 575776004233232386:
        print(message.embeds[0].to_dict())
        if '|' in message.embeds[0].to_dict()['description']:
            member = message.embeds[0].to_dict()['description'].split()[0]
            member_id = member.strip('<@>')
            with(open('data/likers.json', 'r', encoding='utf-8') as f):
                data = load(f)

            if str(member_id) not in data:
                data[member_id] = 1
            else:
                data[member_id] += 1

            with(open('data/likers.json', 'w', encoding='utf-8') as f):
                dump(data, f)

    elif message.channel.id == CONFIG["CHANNEL_EVENTS"]:

        await message.add_reaction(tick)
        await message.add_reaction(like)
        await message.add_reaction(dislike)

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
            await message.reply(f"*Гифки можно отправлять раз в {CONFIG['SETTINGS']['MESSAGES_FOR_GIF']} "
                                    f"сообщений* <a:A_heart1:993383076363239444>", delete_after=3)
            await message.delete()


############################################################################################


@bot.slash_command(description="Сделать заказ в баре")  # команда для заказа в рп баре
async def заказ(inter, сообщение: str):
    channel = bot.get_channel(CONFIG["CHANNEL_RPBAR"])
    barmen_role = "<@&829082636705595433>"

    if inter.channel.id != CONFIG["CHANNEL_RPBAR"]:

        await inter.send(f"Эта команда может быть использована только в канале {channel.mention}!")

    else:

        embed = disnake.Embed(
            title="Новый заказ 📥",
            description=f"{inter.author.mention}\n{сообщение}",
            color=0x2b2d31,
            timestamp=datetime.now()
        )

        embed.set_footer(text="Тоже хочешь заказать что-нибудь? Пропиши /заказ через нашего бота!")

        await channel.send(barmen_role, embed=embed)
        await inter.send(f"Доброго времени суток {inter.author.mention}! Бармен скоро подойдёт 🐥", delete_after=20.0)


############################################################################################


bot.run(CONFIG["TOKEN"])
