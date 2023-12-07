import asyncio
from os import getcwd
import disnake
from disnake.ext import commands
from json import load, dump
from random import randint, shuffle

FOLDER = getcwd()
with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


async def add_failed_scores_counter(scores: int):
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["FAILED_SCORES"] += scores

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def bj_designed_embed_start(embed_dict: dict, inter: disnake.ApplicationCommandInteraction, bet: int):
    embed_dict["title"] = "Привет, приятель"

    await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(1)

    embed_dict["title"] = "Захотел поиграть в BlackJack?"
    embed_dict["description"] = "Ты хотя бы играть то умеешь?"

    await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(2)

    embed_dict["title"] = "Вижу, ты поставил свои честно заработанные очки"
    embed_dict["description"] = f"Аж {bet} оч... пойдёт"

    await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))
    await asyncio.sleep(2)

    embed_dict["title"] = "НАЧИНАЕМ!"
    embed_dict["description"] = ""

    await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))


async def bj_designed_embed(embed_dict: dict, inter: disnake.ApplicationCommandInteraction, current, score):
    embed_dict["title"] = f"Тебе досталась карта {current} "
    embed_dict["description"] = f"У вас {score} оч.\n\n**Будешь брать карту?**"

    await inter.edit_original_response(
        embed=disnake.Embed.from_dict(embed_dict),
        components=[
            disnake.ui.Button(
                label="Взять",
                style=disnake.ButtonStyle.blurple,
                custom_id="take"
            ),
            disnake.ui.Button(
                label="Оставить",
                style=disnake.ButtonStyle.blurple,
                custom_id="stay"
            )
        ]
    )


def random_card(current, score):
    if type(current) is int:
        score += current
    elif current == 'Ace':
        if score <= 10:
            score += 11
        else:
            score += 1
    else:
        score += 10
    return score


class BlackJack(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player = ""
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King', 'Ace'] * 4
        self.score = 0
        self.bot_score = 0
        self.turns = 0
        self.bet = 0
        self.embed_dict = {
            "title": "",
            "description": "",
            "color": 0x2b2d31,
            "author": {
                "name": "BlackJack ♠️"
            },
            "footer": {
                "text": "",
                "icon_url": ""
            }
        }

    @commands.Cog.listener()
    async def on_interaction(self, interaction: disnake.MessageInteraction):
        if interaction.user != self.player and interaction.type is disnake.MessageInteraction:

            await interaction.response.send_message("Это не твоя игра 💀", delete_after=3, ephemeral=True)

        elif "component" in interaction.type:

            if interaction.component.custom_id == "take":
                self.turns += 1
                embed_dict = self.embed_dict
                current = self.deck.pop()
                self.score = random_card(current, self.score)

                await interaction.response.send_message("Ты взял карту", delete_after=2.5, ephemeral=True)

                embed_dict["title"] = f"Тебе досталась карта {current}"
                embed_dict["description"] = f"У тебя {self.score} оч."
                await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))
                await asyncio.sleep(2)

                if self.score > 21:

                    embed_dict["description"] += "\nО нет."

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict), components=[])
                    await asyncio.sleep(2)

                    embed_dict["description"] += f"\n\n**Ты проиграл** и потерял {self.bet} оч."

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                elif self.score == 21:

                    embed_dict["description"] += "\nВОООУ"

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict), components=[])
                    await asyncio.sleep(2)

                    embed_dict["description"] += "\n\n**21-о! Ты выиграл!**"

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))
                    await asyncio.sleep(2)

                    embed_dict["image"] = {"url": "https://media.tenor.com/olRQ2QnTqxQAAAAi/kirby-dance.gif"}

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                else:

                    embed_dict["description"] += f"\n\n**Будешь брать карту?**"

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

            elif interaction.component.custom_id == "stay":
                embed_dict = self.embed_dict

                embed_dict["description"] = f"У тебя {self.score} оч.\n\n**А теперь посмотрим, что выпало боту...**"

                await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict), components=[])
                await asyncio.sleep(2)

                while self.bot_score <= 15:
                    current = self.deck.pop()
                    self.bot_score = random_card(current, self.bot_score)

                    embed_dict["description"] += f"\nБоту выпала карта {current}, у него {self.bot_score} оч."
                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))
                    if self.bot_score > 21:
                        self.bot_score = 0
                        break
                    await asyncio.sleep(1)

                await asyncio.sleep(2)

                if self.bot_score > self.score:

                    embed_dict["description"] += f"\n\n**Бот тебя обыграл. Ты потерял {self.bet} оч.**"

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                elif self.bot_score < self.score:

                    embed_dict["description"] += f"\n\n**Ты выиграл! И получил {self.bet} оч.**"

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

                else:

                    embed_dict["description"] += f"\n\n**Ничья. Ты выиграл {self.bet // 2} оч.**"

                    await interaction.message.edit(embed=disnake.Embed.from_dict(embed_dict))

    @commands.cooldown(1, 10)
    @commands.slash_command(description="Сыграть в BlackJack на свои очки (/rep)")
    async def блекджек(self, inter: disnake.ApplicationCommandInteraction, ставка: int):

        member_id = inter.author.id

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(member_id) not in data:

            await inter.response.send_message("У вас 0 очков 💀", delete_after=5, ephemeral=True)

        else:

            if ставка > data[str(member_id)] or ставка < 1:

                await inter.response.send_message("Вы поставили больше чем у вас есть, либо меньше 1 💀", delete_after=5,
                                                  ephemeral=True)

            else:
                self.player = inter.author
                self.score = 0
                self.bot_score = 0
                self.turns = 0
                self.bet = ставка
                self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King', 'Ace'] * 4
                self.embed_dict = {
                    "title": "",
                    "description": "",
                    "color": 0x2b2d31,
                    "author": {
                        "name": "BlackJack ♠️"
                    },
                    "footer": {
                        "text": f"{inter.guild.name}",
                        "icon_url": f"{inter.guild.icon.url}"
                    }
                }
                embed_dict = self.embed_dict

                data[str(member_id)] -= self.bet

                shuffle(self.deck)

                await bj_designed_embed_start(embed_dict, inter, self.bet)

                current = self.deck.pop()
                self.score = random_card(current, self.score)

                await bj_designed_embed(embed_dict, inter, current, self.score)

                await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))

    @блекджек.error  # Tell the user when they've got a cooldown
    async def on_test_error(self, interaction: disnake.Interaction, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message("Потерпи 💀", delete_after=5, ephemeral=True)


class Roulette(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Крутануть рулеточку на свои РЕАЛЬНЫЕ очки (/rep)")
    async def рулетка(self, inter: disnake.ApplicationCommandInteraction, ставка: int):

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(inter.author.id) in data:
            member_id = inter.author.id

            if ставка > data[str(member_id)] or ставка < 1:

                await inter.response.send_message("Вы поставили больше чем у вас есть, либо меньше 1 💀", delete_after=5,
                                                  ephemeral=True)

            else:
                lucky = randint(0, 100)

                data[str(member_id)] -= ставка

                flag = 1
                if lucky == 100:
                    flag = 3
                    data[str(member_id)] += ставка * 4
                elif lucky >= CONFIG["SETTINGS"]["CHANCE"]:
                    flag = 2
                    data[str(member_id)] += ставка * 2
                elif lucky == 0:
                    flag = 0
                    data[str(member_id)] -= ставка // 2
                member_scores = data[str(member_id)]

                with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
                    dump(data, f)

                embed_dict = {
                    "title": "",
                    "description": f"{inter.author.mention} - `{member_scores}`\nСтавка - `{ставка}`",
                    "color": 0x2b2d31,
                    "author": {
                        "name": "Рулетка на очки 50/50",
                        "icon_url": "https://i.postimg.cc/3JrRXKCz/the-roulette-wheel.jpg"
                    },
                    "footer": {
                        "text": f"{inter.guild.name}",
                        "icon_url": f"{inter.guild.icon.url}"
                    }
                }

                if flag == 1:
                    await add_failed_scores_counter(ставка)

                    embed_dict["title"] += "Вам не повезло 🤕"
                elif flag == 0:
                    await add_failed_scores_counter(ставка + ставка // 2)

                    embed_dict["title"] += "Вам КАТЕГОРИЧЕСКИ НЕ повезло 💔"
                elif flag == 2:
                    embed_dict["title"] += "Вам повезло, cтавка удвоена 🤑"
                elif flag == 3:
                    embed_dict["title"] += "СУПЕРУДАЧА ❤️‍🔥❤️‍🔥❤️‍🔥"

                await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))
        else:

            await inter.response.send_message("У вас 0 очков 💀", delete_after=5, ephemeral=True)

    @рулетка.error  # Tell the user when they've got a cooldown
    async def on_test_error(self, interaction: disnake.Interaction, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message("Потерпи 💀", delete_after=5, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Roulette(bot))
    bot.add_cog(BlackJack(bot))
