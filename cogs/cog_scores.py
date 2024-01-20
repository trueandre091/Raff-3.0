from os import getcwd
import disnake
from disnake.ext import commands

from cogs import counter_functions
from cogs.cog_special import convert_ex_to_lvl, top_create_embed
from cogs.cog_guilds_functions import DB, guild_sets_check, is_none
from bot import set, add, remove

FOLDER = getcwd()


class ScoresOperations(commands.Cog):
    """Where will be scores operations: /add_one, /remove_one, /add_any, /remove_any"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @add.sub_command(
        description="Прибавить очки любому кол-ву участников (упомянуть через пробел)",
    )
    async def scores(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Adding to several members a certain amount of scores"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
        if await is_none(interaction, settings):
            return

        guild = interaction.guild
        members_list = участники.split()
        members_list_values = []

        await counter_functions.count_added_scores(
            количество * len(members_list), interaction.guild.id
        )

        for member in members_list:
            member_id = int(member.strip("<@>"))
            member = guild.get_member(member_id)
            user = await DB.add_user(
                ds_id=member_id, username=member.name, scores=количество
            )
            if user:
                await DB.update_user(
                    ds_id=user.ds_id,
                    username=user.username,
                    scores=user.scores + количество,
                )
                members_list_values.append(user.scores + количество)
            else:
                members_list_values.append(количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} оч. было прибавлено к указанным участникам",
            description="Настоящее количество очков у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            user = await DB.get_user({"ds_id": member_id})
            embed.add_field(
                name=interaction.guild.get_member(member_id),
                value=f"```{user.scores} оч.```",
            )

        await interaction.response.send_message(embed=embed)

    @remove.sub_command(
        description="Вычесть очки у любого кол-ва участников (упомянуть через пробел)",
    )
    async def scores(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участники: str,
        количество: int,
    ):
        """Removing from several members a certain amount of scores"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
        if await is_none(interaction, settings):
            return

        guild = interaction.guild
        members_list = участники.split()
        members_list_values = []

        await counter_functions.count_removed_scores(
            количество * len(members_list), interaction.guild.id
        )

        for member in members_list:
            member_id = int(member.strip("<@>"))
            member = guild.get_member(member_id)
            user = await DB.get_user(ds_id=member_id)
            if not user:
                await DB.update_user(ds_id=member.id, username=member.name, scores=0)
                members_list_values.append(0)
            else:
                if количество >= user.scores:
                    await DB.update_user(
                        ds_id=user.ds_id, username=user.username, scores=0
                    )
                    members_list_values.append(0)
                else:
                    await DB.update_user(
                        ds_id=user.ds_id,
                        username=user.username,
                        scores=user.scores - количество,
                    )
                    members_list_values.append(user.scores - количество)

        members_dict = dict(zip(members_list, members_list_values))
        embed = disnake.Embed(
            title=f"{количество} оч. было вычтено у указанных участников",
            description="Настоящее количество очков у каждого:",
            color=0x2B2D31,
        )
        for member, value in members_dict.items():
            member_id = int(member.strip("<@>"))
            embed.add_field(
                name=interaction.guild.get_member(member_id), value=f"```{value} оч.```"
            )

        await interaction.response.send_message(embed=embed)

    @set.sub_command(
        description="Установить очки любому кол-ву участников (упомянуть через пробел)",
    )
    async def scores(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участник: disnake.Member,
        количество: int,
    ):
        """Setting for a member a certain amount of scores"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
        if await is_none(interaction, settings):
            return

        user = await DB.add_user(
            ds_id=участник.id, username=участник.name, scores=количество
        )
        if user:
            await DB.update_user(
                ds_id=участник.id, username=участник.name, scores=количество
            )

        await interaction.response.send_message(f"У {участник} теперь {количество}")


async def convert(user, embed_dict):
    if user is None:
        embed_dict["fields"][0]["value"] = f"```0 оч.```"
        embed_dict["fields"][1]["value"] = f"```0 лвл.```"
    else:
        embed_dict["fields"][0]["value"] = f"```{user.scores} оч.```"
        embed_dict["fields"][1]["value"] = f"```{await convert_ex_to_lvl(user)} лвл.```"


class SpecialScoresCommands(commands.Cog):
    """Special scores commands: /реп, /топ, /reset"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        description="Показать кол-во очков и уровень у себя / участника"
    )
    async def реп(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        участник: disnake.Member = None,
    ):
        """Showing user's or a somebody's amount of scores"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
        if await is_none(interaction, settings):
            return

        embed_dict = {
            "fields": [
                {"inline": True, "name": "Очки"},
                {"inline": True, "name": "Опыт"},
            ],
            "footer": {"text": interaction.guild.name},
            "thumbnail": {"url": ""},
            "color": 0x2B2D31,
        }
        try:
            embed_dict["footer"]["icon_url"] = interaction.guild.icon.url
        except AttributeError:
            embed_dict["footer"]["icon_url"] = "https://i.postimg.cc/CMsM38p8/1.png"

        if участник:
            embed_dict["title"] = участник.name
            try:
                embed_dict["thumbnail"]["url"] = участник.avatar.url
            except AttributeError:
                embed_dict["thumbnail"]["url"] = "https://i.postimg.cc/CMsM38p8/1.png"
            user = await DB.get_user(ds_id=участник.id)
            await convert(user, embed_dict)
        else:
            embed_dict["title"] = interaction.author.name
            try:
                embed_dict["thumbnail"]["url"] = interaction.author.avatar.url
            except AttributeError:
                embed_dict["thumbnail"]["url"] = "https://i.postimg.cc/CMsM38p8/1.png"
            user = await DB.get_user(ds_id=interaction.author.id)
            await convert(user, embed_dict)

        await interaction.response.send_message(embed=disnake.Embed.from_dict(embed_dict))

    @commands.cooldown(1, 5)
    @commands.slash_command(description="Таблица лидеров по очкам")
    async def топ(self, interaction: disnake.ApplicationCommandInteraction):
        """Sending a leaderboard of members by points"""
        settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
        if await is_none(interaction, settings):
            return

        await interaction.response.send_message("Секунду...")

        embed_dict = {
            "title": "Таблица лидеров по очкам: 📊",
            "description": "",
            "fields": [],
            "color": 0x2B2D31,
            "footer": {
                "text": interaction.guild.name,
            },
        }
        try:
            embed_dict["footer"]["icon_url"] = interaction.guild.icon.url
        except AttributeError:
            embed_dict["footer"]["icon_url"] = "https://i.postimg.cc/CMsM38p8/1.png"
        embed_dict = await top_create_embed(self.bot, settings, embed_dict)

        await interaction.edit_original_response(
            content="", embed=disnake.Embed.from_dict(embed_dict)
        )

    @топ.error
    async def on_test_error(
        self, interaction: disnake.Interaction, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(
                "Нужно немного подождать...", delete_after=5, ephemeral=True
            )

    # @commands.slash_command(
    #     description="Сброс всех очков (пароль)",
    #     default_member_permissions=disnake.Permissions(administrator=True),
    # )
    # async def reset(
    #     self, interaction: disnake.ApplicationCommandInteraction, пароль: int
    # ):
    #     """Resetting scores database and making backup"""
    #     settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
    #     if is_none(interaction, settings):
    #         return
    #
    #     if пароль == settings["GENERAL"]["PASSWORD"]:
    #         top = await DB.get_top_users_by_scores()
    #         top_dict = {}
    #         for user in top:
    #             top_dict[str(user.ds_id)] = [user.username, user.scores]
    #             await DB.update_user(ds_id=user.ds_id, username=user.username, scores=0)
    #
    #         with open(
    #             f"{FOLDER}/data/backups/backup_{date.today()}.json",
    #             "w",
    #             encoding="utf-8",
    #         ) as f:
    #             dump(top_dict, f)
    #         await interaction.response.send_message(
    #             f"База данных сброшена, бэкап создан `{date.today()}`"
    #         )
    #
    #     else:
    #         await interaction.response.send_message(
    #             "Неверный пароль... Ты вор?", delete_after=30
    #         )
    #
    # @commands.slash_command(
    #     description="Вернуть сброшенные данные по бекапу (пароль)",
    #     default_member_permissions=disnake.Permissions(administrator=True),
    # )
    # async def load_backup(
    #     self,
    #     interaction: disnake.ApplicationCommandInteraction,
    #     пароль: int,
    #     backup_date=None,
    # ):
    #     settings = await guild_sets_check(interaction.guild.id, "GENERAL", "SCORES")
    #     if is_none(interaction, settings):
    #         return
    #
    #     if пароль == settings["GENERAL_SETTINGS"]["PASSWORD"]:
    #         if backup_date is None:
    #             for i in range(100):
    #                 day = datetime.timedelta(i)
    #                 try:
    #                     with open(
    #                         f"{FOLDER}/data/backups/backup_{date.today() - day}.json",
    #                         "r",
    #                         encoding="utf-8",
    #                     ) as f:
    #                         data = load(f)
    #                 except json.JSONDecodeError:
    #                     pass
    #                 else:
    #                     break
    #         else:
    #             try:
    #                 with open(
    #                     f"{FOLDER}/data/backups/backup_{backup_date}.json",
    #                     "r",
    #                     encoding="utf-8",
    #                 ) as f:
    #                     data = load(f)
    #             except json.JSONDecodeError:
    #                 await interaction.response.send_message(
    #                     "Бэкап не найден", ephemeral=True
    #                 )
    #                 return
    #
    #         for ds_id, other in data.items():
    #             user = await DB.get_user({"ds_id": int(ds_id)})
    #             if not user:
    #                 await DB.add_user(
    #                     {"ds_id": ds_id, "username": other[0], "scores": other[1]}
    #                 )
    #             else:
    #                 await DB.update_user(
    #                     {
    #                         "ds_id": user.ds_id,
    #                         "username": user.username,
    #                         "scores": other[1],
    #                     }
    #                 )
    #
    #         await interaction.response.send_message("Бекап загружен", ephemeral=True)
    #
    #     else:
    #         await interaction.response.send_message(
    #             "Неверный пароль... Ты вор, сука?", delete_after=30
    #         )


def setup(bot: commands.Bot):
    bot.add_cog(ScoresOperations(bot))
    bot.add_cog(SpecialScoresCommands(bot))
