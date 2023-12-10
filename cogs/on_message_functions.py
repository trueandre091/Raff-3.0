import asyncio
import disnake
from disnake.ext import commands
from datetime import datetime
from cogs import counter_functions


async def moderation(message: disnake.Message, settings: dict, bot: commands.Bot = None):
    """Moderation functions"""
    await gif_moderation(message, settings["GIF"])


async def gif_moderation(message: disnake.Message, settings: dict):
    """Gif moderation"""
    if message.attachments:
        if 'gif' in message.attachments[-1].url:
            channel = message.channel

            flag = False
            skip_first_flag = False
            async for msg in channel.history(limit=settings['MESSAGES_FOR_GIF'] + 1):
                if skip_first_flag:
                    if msg.attachments:
                        if 'gif' in msg.attachments[0].url:
                            flag = True
                            break
                    if 'gif' in msg.content:
                        flag = True
                        break
                skip_first_flag = True

            if flag:
                await counter_functions.count_failed_gif_counter()

                await message.reply(
                    f"{message.author.mention}, гифки можно отправлять раз в {settings['MESSAGES_FOR_GIF']} сообщений",
                    delete_after=5
                )
                await message.delete()

    elif 'gif' in message.content:
        channel = message.channel

        flag = False
        skip_first_flag = False
        async for msg in channel.history(limit=settings['MESSAGES_FOR_GIF'] + 1):
            if skip_first_flag:
                if msg.attachments:
                    if 'gif' in msg.attachments[0].url:
                        flag = True
                        break
                if 'gif' in msg.content:
                    flag = True
                    break
            skip_first_flag = True

        if flag:
            await counter_functions.count_failed_gif_counter()

            await message.reply(
                    f"{message.author.mention}, гифки можно отправлять раз в {settings['MESSAGES_FOR_GIF']} сообщений",
                    delete_after=5
                )
            await message.delete()


async def reactions_thread_check(message: disnake.Message, settings: dict) -> None:
    """Adding reactions and(or) a thread to a message in the certain channels"""
    if str(message.channel.id) in settings["CHANNELS"]:

        channels = settings["CHANNELS"]
        channels_thread = settings["THREAD"]
        reactions = settings["REACTIONS"]
        matched_channels_to_reactions = settings["MATCHED_REACTIONS_TO_CHANNELS"]
        channels = {str(value): key for key, value in channels.items()}
        message_channel_name = channels[str(message.channel.id)]

        if message_channel_name in channels_thread:
            await message.create_thread(name="Комментарии")

        for channel in matched_channels_to_reactions:

            if message_channel_name == channel:
                for reaction in matched_channels_to_reactions[channel]:
                    await message.add_reaction(reactions[reaction])


async def boosts_check(message: disnake.Message, settings: dict) -> None:
    """Checking if it's a boost (and counting number of them through separate function if so)"""
    if message.author.id in settings["BOOST_BOTS"].values():

        if message.author.id == settings["BOOST_BOTS"]["SD.C Monitoring"]:

            flag = True
            skip_first_flag = False
            async for msg in message.channel.history(limit=50):
                if skip_first_flag:
                    if msg.type == disnake.MessageType.application_command and msg.interaction.name == "up":
                        flag = False
                    if msg.author.id == settings["REMINDER"] and "/up" in msg.content:
                        break
                skip_first_flag = False

            if flag:
                print(0)

                await counter_functions.count_users_boosts(message.interaction.user.id)

        if message.author.id == settings["BOOST_BOTS"]["DSMonitoring"]:
            if "Вы успешно лайкнули сервер." in message.embeds[-1].to_dict()["description"]:
                await counter_functions.count_users_boosts(message.interaction.user.id)


async def order_command_check(bot: commands.Bot, message: disnake.Message, settings: dict) -> None:
    """A temporary way to use the slash command '/заказ'"""
    if '/заказ ' in message.content:
        channel = bot.get_channel(settings["CHANNEL"])

        if message.channel.id != channel.id:

            await message.reply(
                f"Эта команда может быть использована только в канале {channel.mention}!", delete_after=5
            )

        else:

            await counter_functions.count_orders_counter()

            barmen_role = f"<@&{settings['BARMEN_ROLE']}>"
            embed = disnake.Embed(
                title="Новый заказ 📥",
                description=f"{message.author.mention}\n{message.content.strip('/заказ ')}",
                color=0x2b2d31,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Тоже хочешь заказать что-нибудь? Пропиши /заказ через нашего бота!")

            await message.reply(
                f"Доброго времени суток {message.author.mention}! Бармен скоро подойдёт 🐥",
                delete_after=10
            )
            await channel.send(barmen_role, embed=embed)
            await message.delete()
