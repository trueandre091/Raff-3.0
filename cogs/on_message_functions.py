import disnake
from disnake.ext import commands
from datetime import datetime
from cogs.counter_functions import *


async def moderation(message: disnake.Message, settings: dict):
    """Moderation functions"""
    if message.channel.id not in settings["COGS"]["MODERATION"]["CHANNELS"]:
        return

    if settings["GENERAL"]["MODERATION"]["GIF"]:
        await gif_moderation(message, settings["COGS"]["MODERATION"]["GIF"])


async def gif_moderation(message: disnake.Message, settings: dict):
    """Gif moderation"""
    flag = False
    if message.attachments:
        if "gif" in message.attachments[-1].url:
            flag = True
    elif "gif" in message.content:
        flag = True

    if flag:
        channel = message.channel

        flag = False
        skip_first_flag = False
        async for msg in channel.history(limit=settings["DELAY"] + 1):
            if skip_first_flag:
                if msg.attachments:
                    if "gif" in msg.attachments[0].url:
                        flag = True
                        break
                if "gif" in msg.content:
                    flag = True
                    break
            skip_first_flag = True

        if flag:
            await count_failed_gif_counter()

            await message.reply(
                f"{message.author.mention}, гифки можно отправлять раз в {settings['DELAY']} сообщений",
                delete_after=5,
            )
            await message.delete()


async def reactions_thread_check(message: disnake.Message, settings: dict) -> None:
    """Adding reactions and(or) a thread to a message in the certain channels"""
    if not settings["GENERAL"]["REACTIONS_THREADS"]:
        return

    settings = settings["REACTIONS_THREADS"]

    if str(message.channel.id) in settings:
        channel_id = message.channel.id

        if settings[str(channel_id)]["THREAD"]:
            await message.create_thread(name="Комментарии")

        if settings[str(channel_id)]["REACTIONS"]:
            for reaction in settings[str(channel_id)]["REACTIONS"]:
                try:
                    await message.add_reaction(reaction)
                except TypeError as E:
                    await message.reply(f"Эмодзи не найден: {E}")
                except disnake.NotFound as E:
                    await message.reply(f"Эмодзи некорректно введён: {E}")


async def boosts_check(message: disnake.Message, settings: dict) -> None:
    """Checking if it's a boost (and counting number of them through separate function if so)"""
    if (
        not settings["GENERAL"]["BOOSTS"]
        or not settings["BOOSTS"]["BOTS"]
        or settings["BOOSTS"]["REMINDER"] is None
    ):
        return

    settings = settings["BOOSTS"]

    if message.author.id in settings["BOTS"].values():
        if message.author.id == settings["BOTS"]["SD.C Monitoring"]:
            flag = True
            skip_first_flag = False
            async for msg in message.channel.history(limit=50):
                if skip_first_flag:
                    if (
                        msg.type == disnake.MessageType.application_command
                        and msg.interaction.name == "up"
                    ):
                        flag = False
                    if msg.author.id == settings["REMINDER"] and "/up" in msg.content:
                        break
                skip_first_flag = False

            if flag:
                await count_users_boosts(message.interaction.user.id, message.guild.id)


async def order_command_check(
    bot: commands.Bot, message: disnake.Message, settings: dict
) -> None:
    """A temporary way to use the slash command '/заказ'"""
    if message.guild.id != 785312593614209055:
        return

    settings = settings["COGS"]["ORDERS"]

    if "/заказ " in message.content:
        channel = bot.get_channel(settings["CHANNEL"])

        if message.channel.id != channel.id:
            await message.reply(
                f"Эта команда может быть использована только в канале {channel.mention}!",
                delete_after=5,
            )

        else:
            await count_orders_counter(message.guild.id)

            barmen_role = f"<@&{settings['ROLE']}>"
            embed = disnake.Embed(
                title="Новый заказ 📥",
                description=f"{message.author.mention}\n{message.content.strip('/заказ ')}",
                color=0x2B2D31,
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text="Тоже хочешь заказать что-нибудь? Пропиши /заказ через нашего бота!"
            )

            await message.reply(
                f"Доброго времени суток {message.author.mention}! Бармен скоро подойдёт 🐥",
                delete_after=10,
            )
            await channel.send(barmen_role, embed=embed)
            await message.delete()
