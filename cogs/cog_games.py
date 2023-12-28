import asyncio
import disnake
from disnake.ext import commands
from random import randint, shuffle

from cogs.guilds_functions import guild_sets_check, GDB, encoder, DB
from cogs.counter_functions import count_lose_scores


def return_corr_embed(interaction):
    embed_dict = {
        "title": "",
        "description": "",
        "color": 0x2B2D31,
        "author": {"name": "BlackJack ♠️"},
        "footer": {
            "text": f"{interaction.guild.name}",
            "icon_url": f"{interaction.guild.icon.url}",
        },
    }
    return embed_dict


async def bj_designed_embed_start(embed_dict: dict, interaction: disnake.ApplicationCommandInteraction, bet: int):
    embed_dict["title"] = "Привет, приятель"

    await interaction.edit_original_response("", embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(1)

    embed_dict["title"] = "Захотел поиграть в BlackJack?"
    embed_dict["description"] = "Ты хотя бы играть то умеешь?"

    await interaction.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(2)

    embed_dict["title"] = "Вижу, ты поставил свои честно заработанные очки"
    embed_dict["description"] = f"Аж {bet} оч... пойдёт"

    await interaction.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(2)

    embed_dict["title"] = "НАЧИНАЕМ!"
    embed_dict["description"] = ""

    await interaction.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))


async def bj_designed_embed(embed_dict: dict, interaction: disnake.ApplicationCommandInteraction, current, score):
    embed_dict["title"] = f"Тебе досталась карта {current} "
    embed_dict["description"] = f"У вас {score} оч.\n\n**Будешь брать карту?**"

    await interaction.edit_original_response(
        embed=disnake.Embed.from_dict(embed_dict),
        components=[
            disnake.ui.Button(label="Взять", style=disnake.ButtonStyle.blurple, custom_id="take"),
            disnake.ui.Button(label="Оставить", style=disnake.ButtonStyle.blurple, custom_id="stay"),
        ],
    )


async def bj_designed_embed_after_take(embed_dict: dict, interaction, current, score):
    embed_dict["title"] = f"Тебе досталась карта {current}"
    embed_dict["description"] = f"У тебя {score} оч."
    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(2)


async def bj_designed_embed_if_lose(embed_dict: dict, interaction, bet):
    embed_dict["description"] += "\nО нет."
    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict), components=[])
    await asyncio.sleep(2)

    embed_dict["description"] += f"\n\n**Ты проиграл** и потерял {bet} оч."
    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))


async def bj_designed_embed_if_21(embed_dict: dict, interaction, bet):
    embed_dict["description"] += "\nВОООУ"
    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict), components=[])
    await asyncio.sleep(2)

    embed_dict["description"] += f"\n\n**21-о! Ты выиграл {bet * 2} оч.!**"
    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(2)

    embed_dict["image"] = {"url": "https://media.tenor.com/olRQ2QnTqxQAAAAi/kirby-dance.gif"}
    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))


def return_scores(current, score):
    """Return scores after convert from voc value_of_card"""
    voc = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "Jack": 2,
        "Queen": 3,
        "King": 4,
    }

    if isinstance(current, int):
        score += current
    elif current == "Ace":
        if score > 10:
            score += 10
        else:
            score += 11
    else:
        score += voc[current]

    return score


class BlackJack(commands.Cog):
    """Class with main logic of BlackJack game

    Functions:
    return_scores - converting name of the card and returning score that player have recieved after first taking

    BlackJack() (блекджек()) - main function with main logic.
    Making checks for user scores and manage them.
    Creates an instance of class for playing BlackJack.

    on_interaction() - listener of events.
    When event is answer for BlackJack and
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(description="Сыграть в BlackJack на свои очки (/rep)")
    async def блекджек(self, interaction: disnake.ApplicationCommandInteraction, ставка: int = None):
        settings = await guild_sets_check(interaction.guild.id, "GENERAL_SETTINGS", "GAMES", "BLACKJACK")
        if settings is None:
            return

        user = await DB.get_user({"ds_id": interaction.author.id})

        author = interaction.author.id
        if ставка:
            if user is None:
                await interaction.response.send_message("У вас 0 очков 💀", delete_after=5, ephemeral=True)

            elif ставка > user.scores or ставка < 1:
                await interaction.response.send_message(
                    "Вы поставили больше чем у вас есть, либо меньше 1 💀",
                    delete_after=5,
                    ephemeral=True,
                )
        else:
            ставка = 1

        game_bj = GameBlackJack(author, commands, ставка)

        await interaction.response.send_message("**BLACKJACK**")

        async for msg in interaction.channel.history(limit=1):
            game_bj.id_message = msg.id

        await bj_designed_embed_start(return_corr_embed(interaction), interaction, ставка)

        game_bj.player_start()

        await bj_designed_embed(
            return_corr_embed(interaction),
            interaction,
            game_bj.current,
            game_bj.score,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.type == disnake.InteractionType.component:
            for obj in GameBlackJack.list_of_objects:
                if obj.id_message == interaction.message.id:
                    if obj.author == interaction.author.id:
                        if "component" in interaction.type:
                            embed_dict = return_corr_embed(interaction)

                            if interaction.component.custom_id == "take":
                                obj.current = obj.deck.pop()
                                obj.score = return_scores(obj.current, obj.score)

                                await interaction.response.send_message(
                                    "Ты взял карту", delete_after=1.5, ephemeral=True
                                )
                                await bj_designed_embed_after_take(embed_dict, interaction, obj.current, obj.score)

                                if obj.score > 21:
                                    await bj_designed_embed_if_lose(embed_dict, interaction, obj.bet)

                                elif obj.score == 21:
                                    await bj_designed_embed_if_21(embed_dict, interaction, obj.bet)

                                else:
                                    embed_dict["description"] += f"\n\n**Будешь брать карту?**"

                                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                            elif interaction.component.custom_id == "stay":
                                embed_dict["description"] = (
                                    f"У тебя {obj.score} оч.\n\n**А теперь посмотрим, что " f"выпало боту...**"
                                )

                                await interaction.message.edit(
                                    embed=disnake.Embed.from_dict(embed_dict),
                                    components=[],
                                )
                                await asyncio.sleep(2)

                                while obj.bot_score <= 15 or obj.score > obj.bot_score:
                                    current = obj.deck.pop()
                                    obj.bot_score = return_scores(current, obj.bot_score)

                                    embed_dict["description"] += (
                                        f"\nБоту выпала карта {current}, " f"у него {obj.bot_score} оч."
                                    )
                                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                                    if obj.bot_score > 21:
                                        obj.bot_score = 0
                                        break
                                    await asyncio.sleep(1)

                                await asyncio.sleep(2)

                                if obj.bot_score > obj.score:
                                    embed_dict["description"] += f"\n\n**Бот тебя обыграл. Ты потерял {obj.bet} оч.**"

                                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                                elif obj.bot_score < obj.score:
                                    embed_dict["description"] += f"\n\n**Ты выиграл! И получил {obj.bet} оч.**"

                                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                                else:
                                    embed_dict["description"] += f"\n\n**Ничья. Ты выиграл {obj.bet // 2} оч.**"

                                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                                GameBlackJack.list_of_objects.remove(obj)
                    else:
                        await interaction.response.send_message(
                            f"Ты не <@{obj.author}> 😱", delete_after=2, ephemeral=True
                        )
                        break


class GameBlackJack:
    """
    Creates an instance of class for playing BlackJack
    Thanks to this class, different users have their own gaming session

    Functions:

    player_start is returning the firs card when the game starting

    return_scores is converting name of the card and returning score that player have received after first taking
    """

    list_of_objects = []

    def __init__(self, author, bot, bet) -> None:
        self.author = author
        self.bot = bot
        self.bet = bet
        self.bot_score = 0
        self.score = 0
        self.id_message = 0
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"] * 4
        self.current = ""
        self.embed_dict = ""

        GameBlackJack.list_of_objects.append(self)

    def player_start(self):
        shuffle(self.deck)

        self.current = self.deck.pop()

        self.score = return_scores(self.current, self.score)


class Roulette(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Крутануть рулеточку на свои РЕАЛЬНЫЕ очки (/rep)")
    async def рулетка(self, interaction: disnake.ApplicationCommandInteraction, ставка: int = None):
        settings = await guild_sets_check(interaction.guild.id, "GENERAL_SETTINGS", "GAMES", "ROULETTE")
        if settings is None:
            return

        settings = settings["COGS_SETTINGS"]["GAMES"]["ROULETTE"]

        user = await DB.get_user({"ds_id": interaction.author.id})

        if user:
            if ставка > user.scores or ставка < 1:
                await interaction.response.send_message(
                    "Вы поставили больше чем у вас есть, либо меньше 1 💀",
                    delete_after=5,
                    ephemeral=True,
                )

            else:
                lucky = randint(0, 100)

                await DB.update_user(
                    {
                        "ds_id": user.ds_id,
                        "username": user.username,
                        "scores": user.scores - ставка,
                    }
                )

                flag = 1
                if lucky == 100:
                    flag = 3
                    await DB.update_user(
                        {
                            "ds_id": user.ds_id,
                            "username": user.username,
                            "scores": user.scores + ставка,
                        }
                    )
                elif lucky >= settings["CHANCE"]:
                    flag = 2
                    await DB.update_user(
                        {
                            "ds_id": user.ds_id,
                            "username": user.username,
                            "scores": user.scores + ставка * 2,
                        }
                    )
                elif lucky == 0:
                    flag = 0
                user = await DB.get_user({"ds_id": user.ds_id})

                embed_dict = {
                    "title": "",
                    "description": f"{interaction.author.mention} - `{user.scores}`\nСтавка - `{ставка}`",
                    "color": 0x2B2D31,
                    "author": {
                        "name": "Рулетка на очки 50/50",
                        "icon_url": "https://i.postimg.cc/3JrRXKCz/the-roulette-wheel.jpg",
                    },
                    "footer": {
                        "text": f"{interaction.guild.name}",
                        "icon_url": f"{interaction.guild.icon.url}",
                    },
                }

                if flag == 1:
                    await count_lose_scores(ставка)

                    embed_dict["title"] += "Вам не повезло 🤕"
                elif flag == 0:
                    await count_lose_scores(ставка)

                    embed_dict["title"] += "Вам КАТЕГОРИЧЕСКИ НЕ повезло 💔"
                elif flag == 2:
                    embed_dict["title"] += "Вам повезло, cтавка удвоена 🤑"
                elif flag == 3:
                    embed_dict["title"] += "СУПЕРУДАЧА ❤️‍🔥❤️‍🔥❤️‍🔥"

                await interaction.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
        else:
            await interaction.response.send_message("У вас 0 очков 💀", delete_after=5, ephemeral=True)

    @рулетка.error
    async def on_test_error(self, interaction: disnake.Interaction, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message("Потерпи 💀", delete_after=5, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(BlackJack(bot))
    bot.add_cog(Roulette(bot))
