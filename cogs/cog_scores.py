from os import getcwd
import disnake
from disnake.ext import commands
from json import load, dump
from datetime import date

FOLDER = getcwd()
with (open(f"{FOLDER}/config.json", "r", encoding="utf-8") as file):
    CONFIG = load(file)


async def add_added_scores_counter(scores: int):
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["ADDED_SCORES"] += scores

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def add_removed_scores_counter(scores: int):
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["REMOVED_SCORES"] += scores

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


def add_to_top(member_id: str, amount: int):
    with (open(f"{FOLDER}/data/top.json", "r", encoding="utf-8") as f):
        top = load(f)
    top[member_id] = amount
    with (open(f"{FOLDER}/data/top.json", "w", encoding="utf-8") as f):
        dump(top, f)


class ScoresOperations(commands.Cog):
    """Where will be scores operations"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Показать кол-во очков у себя / участника")
    async def реп(self, inter: disnake.ApplicationCommandInteraction, участник: disnake.Member = None):

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        name1 = "Очки"
        name2 = "Место в топе"
        value1 = f"```0 оч.```"
        value1_2 = ""
        embed1 = ""
        embed2 = ""

        if участник is not None:
            value1_2 = f"```{data[str(участник.id)]} оч.```"
            embed2 = disnake.Embed(
                title=f"{участник}",
                color=0x2b2d31
            )
            try:
                embed2.set_thumbnail(url=участник.avatar.url)
            except AttributeError:
                embed2.set_thumbnail(url='https://i.postimg.cc/CMsM38p8/1.png')
            embed2.set_footer(
                text=inter.guild.name,
                icon_url=inter.guild.icon.url
            )
        else:
            embed1 = disnake.Embed(
                title=f"{inter.author}",
                color=0x2b2d31
            )
            try:
                embed1.set_thumbnail(url=inter.author.avatar.url)
            except AttributeError:
                embed1.set_thumbnail(url='https://i.postimg.cc/CMsM38p8/1.png')
            embed1.set_footer(
                text=inter.guild.name,
                icon_url=inter.guild.icon.url
            )

        value2 = f"```#```"

        if участник is None:
            if str(inter.author.id) not in data:

                embed1.set_thumbnail(url=inter.author.avatar.url)
                embed1.add_field(
                    name=name1,
                    value=value1
                )
                embed1.add_field(
                    name=name2,
                    value=value2
                )

                await inter.response.send_message(embed=embed1)

            else:

                embed1.add_field(
                    name=name1,
                    value=f"```{data[str(inter.author.id)]} оч.```"
                )
                embed1.add_field(
                    name=name2,
                    value=value2
                )

                await inter.response.send_message(embed=embed1)

        else:
            if str(участник.id) not in data:

                embed2.add_field(
                    name=name1,
                    value=value1
                )
                embed2.add_field(
                    name=name2,
                    value=value2
                )

                await inter.response.send_message(embed=embed2)

            else:

                embed2.add_field(
                    name=name1,
                    value=value1_2
                )
                embed2.add_field(
                    name=name2,
                    value=value2
                )

                await inter.response.send_message(embed=embed2)

    ############################################################################################

    @commands.slash_command(
        description="Прибавить очки 1 участнику",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def add_just_one(
            self, inter: disnake.ApplicationCommandInteraction,
            участник: disnake.Member, количество: int
    ):

        await add_added_scores_counter(количество)

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(участник.id) not in data:
            data[str(участник.id)] = количество
        else:
            data[str(участник.id)] += количество

        await inter.response.send_message(f"Теперь у {участник} {data[str(участник.id)]} оч.")

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

    @commands.slash_command(
        description="Вычесть очки у 1 участника",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def remove_just_one(
            self, inter: disnake.ApplicationCommandInteraction,
            участник: disnake.Member, количество: int
    ):

        await add_removed_scores_counter(количество)

        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        if str(участник.id) not in data:
            await inter.response.send_message("У участника 0 очков, куда меньше?...")
        else:
            if количество >= data[str(участник.id)]:
                data[str(участник.id)] = 0
            else:
                data[str(участник.id)] -= количество

        await inter.response.send_message(f"Теперь у {участник} {data[str(участник.id)]} оч.")

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

    @commands.slash_command(
        description="Вычесть очки у любого кол-ва участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def remove_any(self, inter: disnake.ApplicationCommandInteraction, участники: str, количество: int):
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        members_list = участники.split()
        members_list_values = []

        await add_removed_scores_counter(количество * len(members_list))

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

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} оч. было вычтено у указанных участников",
            description="Настоящее количество очков у каждого:",
            color=0x2b2d31
        )
        for member, value in members_dict.items():
            member_id = int(member.strip('<@>'))

            embed.add_field(name=await self.bot.fetch_user(member_id), value=f"```{value} оч.```")

        await inter.response.send_message(embed=embed)

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)

    @commands.slash_command(
        description="Прибавить очки любому кол-ву участников (упомянуть через пробел)",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def add_any(self, inter: disnake.ApplicationCommandInteraction, участники: str, количество: int):
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        members_list = участники.split()
        members_list_values = []

        await add_added_scores_counter(количество * len(members_list))

        for member in members_list:
            member_id = int(member.strip('<@>'))
            if str(member_id) not in data:
                data[str(member_id)] = количество
                members_list_values.append(data[str(member_id)])
            else:
                data[str(member_id)] += количество
                members_list_values.append(data[str(member_id)])

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} оч. было прибавлено к указанным участникам",
            description="Настоящее количество очков у каждого:",
            color=0x2b2d31
        )
        for member, value in members_dict.items():
            member_id = int(member.strip('<@>'))

            embed.add_field(name=await self.bot.fetch_user(member_id), value=f"```{value} оч.```")

        await inter.response.send_message(embed=embed)

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)
            
    @commands.slash_command(
        description="Установить определённое кол-во очков участнику",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def set_just_one(
            self,
            inter: disnake.ApplicationCommandInteraction,
            участник: disnake.Member, количество: int
    ):
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        data[str(участник.id)] = количество

        with (open(f"{FOLDER}/data/users_data.json", "w", encoding="utf-8") as f):
            dump(data, f)
            
        await inter.response.send_message(f"У {участник} теперь {количество}")

    ############################################################################################

    @commands.slash_command(
        description="Таблица лидеров по очкам"
    )
    async def топ(self, inter: disnake.ApplicationCommandInteraction):
        with (open(f"{FOLDER}/data/users_data.json", "r", encoding="utf-8") as f):
            data = load(f)

        sort_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        data = dict(sort_data)

        guild = self.bot.get_guild(CONFIG["GUILD_ID"])
        
        nulls = []
        for key, value in data.items():
            if value == 0:
                nulls.append(key)
        for key in nulls:
            data.pop(key)

        embed_dict = {
            'title': 'Таблица лидеров по очкам: 📊',
            'description': '',
            'fields': [],
            'color': 0x2b2d31,
            'footer': {'text': inter.guild.name, 'icon_url': inter.guild.icon.url}
        }

        await inter.response.send_message(embed=disnake.Embed.from_dict(embed_dict))

        first_lvl_members = []
        third_lvl_members = []
        fifth_lvl_members = []
        amount1 = CONFIG["SETTINGS"]["AMOUNT_TO_FIRST_LVL"]
        amount2 = CONFIG["SETTINGS"]["AMOUNT_TO_THIRD_LVL"]
        amount3 = CONFIG["SETTINGS"]["AMOUNT_TO_FIFTH_LVL"]

        flag = False
        flag1 = False
        flag2 = False
        flag3 = False
        c = 1
        for key, value in data.items():
            member = guild.get_member(int(key))

            embed_dict['description'] += f"`{c}.` {member.mention} — `{value} оч.`\n"
            await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))
            if amount1 <= value < amount2:
                flag1 = True
                first_lvl_members.append(key)
            elif amount2 <= value < amount3:
                flag2 = True
                third_lvl_members.append(key)
            elif amount3 <= value:
                flag3 = True
                fifth_lvl_members.append(key)
            c += 1

        c = 0
        if flag1 or flag2 or flag3:
            embed_dict['description'] += "\n**Получат роли**"

        if flag1:
            embed_dict['fields'].append({'name': '1-го уровня:', 'value': '', 'inline': True})
            for key in first_lvl_members:
                member = guild.get_member(int(key))
                embed_dict['fields'][c]['value'] += f"{member.mention} "
            c += 1

        if flag2:
            embed_dict['fields'].append({'name': '3-го уровня:', 'value': '', 'inline': True})
            for key in third_lvl_members:
                member = guild.get_member(int(key))
                embed_dict['fields'][c]['value'] += f"{member.mention} "
            c += 1

        if flag3:
            embed_dict['fields'].append({'name': '5-го уровня:', 'value': '', 'inline': True})
            for key in fifth_lvl_members:
                member = guild.get_member(int(key))
                embed_dict['fields'][c]['value'] += f"{member.mention} "
            c += 1

        await inter.edit_original_response(embed=disnake.Embed.from_dict(embed_dict))

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
        if пароль == CONFIG["SETTINGS"]["PASSWORD"]:
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
