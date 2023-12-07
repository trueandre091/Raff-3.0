from datetime import datetime
import disnake
from disnake.ext import commands
from json import load, dump

import config as cfg
from cogs.counter_functions import *
from cogs.on_message_functions import *

bot = commands.Bot(command_prefix="none", help_command=None, intents=disnake.Intents.all(), chunk_guilds_at_startup=False)

# bot.load_extension("cogs")


@bot.event
async def on_ready():
    '''Bot writes in console when it starts'''
    print(f"Bot {bot.user} is ready to work!")


############################################################################################


@bot.event
async def on_member_join(member):
    """Greeting newbies when they come"""
    settings = cfg.WELCOME_SETTINGS

    channel = bot.get_channel(settings["CHANNEL"])
    member = str(member.mention)

    embed_dict = {
        "title": settings["TITLE"],
        "description": member + settings["EMBED"]["DESCRIPTION"],
        "color": settings["EMBED"]["COLOR"],
        "timestamp": datetime.now(),
    }

    try:
        embed_dict["thumbnail"]["url"] = member.avatar.url
    except AttributeError:
        embed_dict["thumbnail"]["url"] = settings["AVATAR_IF_ERROR"]

    embed_dict["image"]["url"] = settings["BACKGROUND_IMAGE"]

    await channel.send(embed=disnake.Embed.from_dict(embed_dict))


@bot.event
async def on_member_remove(member):
    """Farewell to members when they leave"""
    settings = cfg.FAREWELL_SETTINGS

    channel = bot.get_channel(settings["CHANNEL"])
    await channel.send(f"{member.mention} / {member.name} / {member.nick} ушёл.")


############################################################################################


@bot.event  # автосоздание веток и реакций (лайк и дизлайк)
async def on_message(message):
    """On every sent message functions"""

    boost_bots = cfg.BOOST_BOTS
    author_id = message.author.id

    count_every_message(message)

    ############################################################################################

    await reactions_thread_check(message, cfg.ADDING_REACTIONS_THREADS)

    await boosts_check(message, cfg.BOOSTS_COUNTING)

    # if message.type == disnake.MessageType.application_command and author_id in boost_bots:

    #     if author_id == boost_bots[1]:
    #         flag = True
    #         skip_first_flag = False
    #         async for msg in message.channel.history(limit=50):
    #             if skip_first_flag:
    #                 if msg.type == disnake.MessageType.application_command and msg.interaction.name == "up":
    #                     flag = False
    #                 if msg.author.id == 478321260481478677 and "/up" in msg.content:
    #                     break
    #             skip_first_flag = False
    #         if flag:

    #             member_id = message.interaction.user.id

    #             with(open('data/counters.json', 'r', encoding='utf-8') as f):
    #                 data = load(f)

    #             if str(member_id) not in data["LIKERS"]:
    #                 data["LIKERS"][str(member_id)] = 1
    #             else:
    #                 data["LIKERS"][str(member_id)] += 1

    #             with(open('data/counters.json', 'w', encoding='utf-8') as f):
    #                 dump(data, f)

    #     if author_id == boost_bots[0]:
    #         if "Вы успешно лайкнули сервер." in message.embeds[-1].to_dict()["description"]:

    #             member_id = message.interaction.user.id

    #             with(open('data/counters.json', 'r', encoding='utf-8') as f):
    #                 data = load(f)

    #             if str(member_id) not in data["LIKERS"]:
    #                 data["LIKERS"][str(member_id)] = 1
    #             else:
    #                 data["LIKERS"][str(member_id)] += 1

    #             with(open('data/counters.json', 'w', encoding='utf-8') as f):
    #                 dump(data, f)


    ############################################################################################

    if '/заказ' in message.content.split()[0]:

        channel = bot.get_channel(cfg.CHANNELS_SETTING["CHANNEL_RPBAR"])
        barmen_role = "<@&829082636705595433>"

        if message.channel.id != cfg.CHANNELS_SETTING["CHANNEL_RPBAR"]:

            await message.reply(
                f"Эта команда может быть использована только в канале {channel.mention}!",
                delete_after=5
            )

        else:

            counter_fn.count_orders_counter()

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
            async for msg in channel.history(limit=cfg.SETTINGS["MESSAGES_FOR_GIF"] + 1):
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

                counter_fn.count_failed_gif_counter()

                await message.reply(f"Гифки можно отправлять раз в {cfg.SETTINGS['MESSAGES_FOR_GIF']} "
                                    f"сообщений <a:A_heart1:993383076363239444>", delete_after=3)
                await message.delete()

    elif 'gif' in message.content:
        channel = message.channel

        flag = False
        c = False
        async for msg in channel.history(limit=cfg.SETTINGS["MESSAGES_FOR_GIF"] + 1):
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
            counter_fn.count_failed_gif_counter()

            await message.reply(f"Гифки можно отправлять раз в {cfg.SETTINGS['MESSAGES_FOR_GIF']} "
                                f"сообщений <a:A_heart1:993383076363239444>", delete_after=3)
            await message.delete()


############################################################################################


bot.run(cfg.TOKEN)
