import disnake
from cogs import counter_functions


async def reactions_thread_check(message: disnake.Message, settings_dict) -> None:

    if str(message.channel.id) in settings_dict["CHANNELS"]:
    
        channels = settings_dict["CHANNELS"]
        channels_thread = settings_dict["THREAD"]
        reactions = settings_dict["REACTIONS"]
        matched_channels_to_reactions = settings_dict["MATCHED_REACTIONS_TO_CHANNELS"]

        message_channel_name = channels[str(message.channel.id)]
        print(message_channel_name)

        if message_channel_name in channels_thread:

            await message.create_thread(name="Комментарии")
        
        for channel in matched_channels_to_reactions:
            
            if message_channel_name == channel:
                for reaction in matched_channels_to_reactions[channel]:

                    await message.add_reaction(reactions[reaction])


async def boosts_check(message: disnake.Message, settings_dict) -> None:

    if message.author.id in settings_dict["BOOST_BOTS"].values():

        if message.author.id == settings_dict["BOOST_BOTS"]["SD.C Monitoring"]:

            flag = True
            skip_first_flag = False 
            async for msg in message.channel.history(limit=50):
                if skip_first_flag:
                    if msg.type == disnake.MessageType.application_command and msg.interaction.name == "up":
                        flag = False
                    if msg.author.id == settings_dict["REMINDER"] and "/up" in msg.content:
                        break
                skip_first_flag = False

            if flag:
                print(0)

                counter_functions.count_users_boosts(message.interaction.user.id)

        if message.author.id == settings_dict["BOOST_BOTS"]["DSMonitoring"]:
            if "Вы успешно лайкнули сервер." in message.embeds[-1].to_dict()["description"]:

                counter_functions.count_users_boosts(message.interaction.user.id)


if '/заказ' in message.content:

        channel = bot.get_channel(cfg.CHANNELS_SETTINGS["CHANNEL_RPBAR"])
        barmen_role = "<@&829082636705595433>"

        if message.channel.id != cfg.CHANNELS_SETTINGS["CHANNEL_RPBAR"]:

            await message.reply(
                f"Эта команда может быть использована только в канале {channel.mention}!",
                delete_after=5
            )

        else:

            count_orders_counter()

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
