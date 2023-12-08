from os import getcwd
import disnake
from disnake.ext import commands
from json import load, dump
from datetime import date

import config as cfg
from cogs import counter_functions
FOLDER = getcwd()


async def top_create_embed(bot: commands.Bot, embed_dict: dict):
    """Creating an embed of leaderboard of members by scores"""
    guild = bot.get_guild(cfg.GUILD_ID)

    with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
        data = load(f)
    sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    data = dict(sort_data)

    nulls = []
    for key, value in data.items():
        if value == 0:
            nulls.append(key)
    for key in nulls:
        data.pop(key)

    first_lvl_members, third_lvl_members, fifth_lvl_members = [], [], []
    amount1 = cfg.SETTINGS["AMOUNT_TO_FIRST_LVL"]
    amount2 = cfg.SETTINGS["AMOUNT_TO_THIRD_LVL"]
    amount3 = cfg.SETTINGS["AMOUNT_TO_FIFTH_LVL"]

    flag1, flag2, flag3 = False, False, False
    place = 0
    for key, value in data.items():
        member = guild.get_member(int(key))
        embed_dict['description'] += f"`{place + 1}.` {member.mention} — `{value} оч.`\n"
        if amount1 <= value < amount2:
            flag1 = True
            first_lvl_members.append(key)
        elif amount2 <= value < amount3:
            flag2 = True
            third_lvl_members.append(key)
        elif amount3 <= value:
            flag3 = True
            fifth_lvl_members.append(key)
        place += 1

    if flag1 or flag2 or flag3:
        embed_dict['description'] += "\n**Получат роли**"

    index_of_field = 0
    if flag1:
        embed_dict['fields'].append({'name': '1-го уровня:', 'value': '', 'inline': True})
        for key in first_lvl_members:
            member = guild.get_member(int(key))
            embed_dict['fields'][index_of_field]['value'] += f"{member.mention} "
        index_of_field += 1

    if flag2:
        embed_dict['fields'].append({'name': '3-го уровня:', 'value': '', 'inline': True})
        for key in third_lvl_members:
            member = guild.get_member(int(key))
            embed_dict['fields'][index_of_field]['value'] += f"{member.mention} "
        index_of_field += 1

    if flag3:
        embed_dict['fields'].append({'name': '5-го уровня:', 'value': '', 'inline': True})
        for key in fifth_lvl_members:
            member = guild.get_member(int(key))
            embed_dict['fields'][index_of_field]['value'] += f"{member.mention} "
        index_of_field += 1

    return embed_dict


class ScoresOperations(commands.Cog):
    """Where will be scores operations"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Показать кол-во очков у себя / участника")
    async def реп(self, interaction: disnake.ApplicationCommandInteraction, участник: disnake.Member = None):
        """Showing user's or a somebody's amount of scores"""
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        embed_dict = {
            'fields': [{'name': 'Очки'}],
            'footer': {'text': interaction.guild.name, 'icon_url': interaction.guild.icon.url},
            'color': 0x2b2d31
        }
        if участник:
            embed_dict['title'] = участник.name
            try:
                embed_dict['thumbnail'] = f'{участник}'
            except AttributeError:
                embed_dict['thumbnail'] = 'https://i.postimg.cc/CMsM38p8/1.png'
            try:
                embed_dict['fields'][0]['value'] = f"```{data[str(участник.id)]} оч.```"
            except:
                embed_dict['fields'][0]['value'] = f'```0 оч.```'
        else:
            embed_dict['title'] = f'{interaction.author}'
            try:
                embed_dict['thumbnail'] = f'{interaction.author}'
            except AttributeError:
                embed_dict['thumbnail'] = 'https://i.postimg.cc/CMsM38p8/1.png'
            try:
                embed_dict['fields'][0]['value'] = f"```{data[str(interaction.author.id)]} оч.```"
            except:
                embed_dict['fields'][0]['value'] = f'```0 оч.```'

        await interaction.response.send_message(embed=disnake.Embed.from_dict(embed_dict))

    ############################################################################################

    @commands.slash_command(
        description="Прибавить очки 1 участнику",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def add_just_one(
            self, inter: disnake.ApplicationCommandInteraction,
            участник: disnake.Member, количество: int
    ):
        """Adding to a member a certain amount of scores"""
        await counter_functions.count_added_scores(количество)

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(участник.id) not in data:
            data[str(участник.id)] = количество
        else:
            data[str(участник.id)] += количество

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

        await inter.response.send_message(f"Теперь у {участник} {data[str(участник.id)]} оч.")

    @commands.slash_command(
        description="Вычесть очки у 1 участника",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def remove_just_one(
            self, inter: disnake.ApplicationCommandInteraction,
            участник: disnake.Member, количество: int
    ):
        """Removing from a member a certain amount of scores"""
        await counter_functions.count_removed_scores(количество)

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(участник.id) not in data:
            await inter.response.send_message("У участника 0 очков, куда меньше?...")
        else:
            if количество >= data[str(участник.id)]:
                data[str(участник.id)] = 0
            else:
                data[str(участник.id)] -= количество

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

        await inter.response.send_message(f"Теперь у {участник} {data[str(участник.id)]} оч.")

    @commands.slash_command(
        description="Вычесть очки у любого кол-ва участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def remove_any(self, interaction: disnake.ApplicationCommandInteraction, участники: str, количество: int):
        """Removing from several members a certain amount of scores"""
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        members_list = участники.split()
        members_list_values = []

        await counter_functions.count_removed_scores(количество * len(members_list))

        for member in members_list:
            member_id = int(member.strip('<@>'))
            if str(member_id) not in data:
                members_list_values.append(0)
            else:
                if количество >= data[str(member_id)]:
                    data.pop(str(member_id))
                    members_list_values.append(0)
                else:
                    data[str(member_id)] -= количество
                    members_list_values.append(data[str(member_id)])

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} оч. было вычтено у указанных участников",
            description="Настоящее количество очков у каждого:",
            color=0x2b2d31
        )
        for member, value in members_dict.items():
            member_id = int(member.strip('<@>'))
            embed.add_field(name=interaction.guild.get_member(member_id), value=f"```{value} оч.```")

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(
        description="Прибавить очки любому кол-ву участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def add_any(self, interaction: disnake.ApplicationCommandInteraction, участники: str, количество: int):
        """Adding to several members a certain amount of scores"""
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        members_list = участники.split()
        members_list_values = []

        await counter_functions.count_added_scores(количество * len(members_list))

        for member in members_list:
            member_id = int(member.strip('<@>'))
            if str(member_id) not in data:
                data[str(member_id)] = количество
                members_list_values.append(data[str(member_id)])
            else:
                data[str(member_id)] += количество
                members_list_values.append(data[str(member_id)])

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} оч. было прибавлено к указанным участникам",
            description="Настоящее количество очков у каждого:",
            color=0x2b2d31
        )
        for member, value in members_dict.items():
            member_id = int(member.strip('<@>'))
            embed.add_field(name=interaction.guild.get_member(member_id), value=f"```{value} оч.```")

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(
        description="Установить определённое кол-во очков участнику",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def set_just_one(
            self,
            inter: disnake.ApplicationCommandInteraction,
            участник: disnake.Member, количество: int
    ):
        """Setting for a member a certain amount of scores"""
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        data[str(участник.id)] = количество

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

        await inter.response.send_message(f"У {участник} теперь {количество}")

    ############################################################################################

    @commands.slash_command(description="Таблица лидеров по очкам")
    async def топ(self, interaction: disnake.ApplicationCommandInteraction):
        """Sending a leaderboard of members by points"""
        await interaction.response.send_message('...')

        embed_dict = {
            'title': 'Таблица лидеров по очкам: 📊',
            'description': '',
            'fields': [],
            'color': 0x2b2d31,
            'footer': {'text': interaction.guild.name, 'icon_url': interaction.guild.icon.url}
        }
        embed_dict = await top_create_embed(self.bot, embed_dict)

        await interaction.edit_original_response(content='', embed=disnake.Embed.from_dict(embed_dict))

    @топ.error
    async def on_test_error(self, interaction: disnake.Interaction, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message("Нужно немного подождать...", delete_after=5, ephemeral=True)


class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Сброс всех очков (пароль)",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def reset(self, inter: disnake.ApplicationCommandInteraction, пароль: int):
        """Resetting scores database and making backup"""
        if пароль == cfg.SETTINGS["PASSWORD"]:
            with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
                data = load(f)

            with (open(f"{FOLDER}/data/backups/backup_{date.today()}.json", 'w', encoding="utf-8") as f):
                dump(data, f)

            with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
                dump({}, f)

            await inter.response.send_message(f"База данных сброшена, бэкап создан `{date.today()}`")

        else:

            await inter.response.send_message("Неверный пароль... Ты вор, сука?", delete_after=30)


def setup(bot: commands.Bot):
    bot.add_cog(ScoresOperations(bot))
    bot.add_cog(Special(bot))
