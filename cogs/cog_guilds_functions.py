from disnake.ext import commands, tasks
from DB.JSONEnc import JsonEncoder
from DB.DataBase import GuildsDBase, UserDBase, RelationshipsDBase
from DB.models import Guilds

DB = UserDBase()
GDB = GuildsDBase()
RDB = RelationshipsDBase()
encoder = JsonEncoder()


async def guild_sets_check(
    guild_id: int,
    checking_set_1: str = None,
    checking_set_2: str = None,
    checking_set_3: str = None,
) -> dict:
    """Checking if guild exists in DB or if certain functions are turned on guild"""
    guild = await GDB.get_guild(guild_id=guild_id)
    if guild:
        guild = encoder.code_from_json(guild.guild_sets)
        if checking_set_1 and checking_set_2 and checking_set_3:
            if guild[checking_set_1][checking_set_2][checking_set_3]:
                return guild
        elif checking_set_1 and checking_set_2:
            if guild[checking_set_1][checking_set_2]:
                return guild
        elif checking_set_1:
            if guild[checking_set_1]:
                return guild
        else:
            return guild


async def find_guilds_by_param(
    bot: commands.Bot,
    checking_set_1: str = False,
    checking_set_2: str = False,
    checking_set_3: str = False,
    encode: bool = True,
) -> list[Guilds | dict]:
    """Finding servers by certain parameter, returns a list"""
    list_of_guilds = []
    for guild in bot.guilds:
        list_of_guilds.append(guild.id)
    list_temp = []
    for guild in list_of_guilds:
        list_temp.append(await GDB.get_guild_with_users(guild_id=guild))
    if list_temp is None:
        return []

    list_res = []
    for guild in list_temp:
        if guild:
            guild_dict = encoder.code_from_json(guild.guild_sets)
            if checking_set_1 and checking_set_2 and checking_set_3:
                if guild_dict[checking_set_1][checking_set_2][checking_set_3]:
                    if encode:
                        list_res.append(guild_dict)
                    else:
                        list_res.append(guild)
            elif checking_set_1 and checking_set_2:
                if guild_dict[checking_set_1][checking_set_2]:
                    if encode:
                        list_res.append(guild_dict)
                    else:
                        list_res.append(guild)
            elif checking_set_1:
                if guild_dict[checking_set_1]:
                    if encode:
                        list_res.append(guild_dict)
                    else:
                        list_res.append(guild)
            else:
                if encode:
                    list_res.append(guild_dict)
                else:
                    list_res.append(guild)
    return list_res


async def is_none(interaction, settings):
    if settings is None:
        await interaction.response.send_message(
            "Данная функция отключена на сервере", ephemeral=True
        )
        return True


class AutoRelationshipsAdding(commands.Cog):
    """Task, that checks for new members and adds them to RDB if they are every 5 minutes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auto_relations_adding.start()

    @tasks.loop(minutes=10)
    async def auto_relations_adding(self):
        users = await DB.get_all_users_with_guilds()
        if users is None:
            return

        for guild in self.bot.guilds:
            rdb_guild = await GDB.get_guild_with_users(guild_id=guild.id)
            if rdb_guild is None:
                continue

            for user in users:
                if guild.get_member(user.ds_id):
                    await RDB.add_relationship(
                        users=[{"ds_id": user.ds_id}],
                        guilds=[{"guild_id": guild.id}],
                    )

            for user in rdb_guild.users:
                if guild.get_member(user.ds_id) is None:
                    await RDB.delete_relationship(
                        users=[{"ds_id": user.ds_id}],
                        guilds=[{"guild_id": guild.id}],
                    )

    @auto_relations_adding.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(AutoRelationshipsAdding(bot))


dicts = {
    "GUILD_ID": 785312593614209055,
    "GENERAL": {
        "PASSWORD": 152364,
        "WELCOME": False,
        "FAREWELL": False,
        "MODERATION": {"GIF": False},
        "AUTOUPDATE": {"MESSAGES": False, "SCORES": False},
        "NEAREST_EVENTS": False,
        "EXPERIENCE": False,
        "GAMES": {"ALL_GAMES": False, "BLACKJACK": False, "ROULETTE": False},
        "ORDERS": False,
        "REQUESTS": False,
        "SCORES": False,
        "BOOSTS_COUNTING": False,
        "REACTIONS_THREADS": False,
        "ROLES": False,
        "EVENT_REWARDING": False,
    },
    ###########################################################
    "COGS": {
        "WELCOME": {
            "CHANNEL": None,
            "EMBED": {
                "TITLE": "Добро пожаловать на сервер!  💌",
                "DESCRIPTION": "{member.mention}, рады тебя видеть на нашем сервере!\n",
                "IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
                "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
                "COLOR": 0x2B2D31,
            },
        },
        "FAREWELL": {
            "CHANNEL": None,
            "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл с сервера!",
        },
        "REACTIONS_THREADS": {
            "858731672677515294": {"REACTIONS": [], "THREAD": True},
            "785312596546813976": {
                "REACTIONS": [
                    "<:B_00like:1001544330613375026>",
                    "<:B_00likenot:1001544295532204082>",
                ],
                "THREAD": True,
            },
            "1160687361269694505": {
                "REACTIONS": [
                    "<:B_00like:1001544330613375026>",
                    "<:B_00likenot:1001544295532204082>",
                    "✅",
                ],
                "THREAD": False,
            },
        },
        "MODERATION": {"CHANNELS": [], "GIF": {"DELAY": 10}},
        "SCORES": {
            "REWARDS": [
                {"ROLE": 996015029495271505, "AMOUNT": 8},
                {"ROLE": 996014817410293812, "AMOUNT": 12},
                {"ROLE": 840523873447706624, "AMOUNT": 18},
            ],
        },
        "EXPERIENCE": {
            "REWARDS": [
                {"ROLE": 785933016207720538, "AMOUNT": 1},
                {"ROLE": 785934178351972401, "AMOUNT": 5},
                {"ROLE": 785934175164432426, "AMOUNT": 10},
                {"ROLE": 785935023550759013, "AMOUNT": 20},
                {"ROLE": 785935030953705544, "AMOUNT": 30},
                {"ROLE": 785936131539730453, "AMOUNT": 40},
                {"ROLE": 785936148974272543, "AMOUNT": 45},
                {"ROLE": 785938004391886859, "AMOUNT": 50},
                {"ROLE": 840514241970569236, "AMOUNT": 55},
                {"ROLE": 840514253600325632, "AMOUNT": 60},
                {"ROLE": 840515445320581139, "AMOUNT": 65},
                {"ROLE": 840515310770847745, "AMOUNT": 70},
            ]
        },
        "AUTOUPDATE": {
            "CHANNEL": None,
            "MESSAGES": {"LIMIT": 10},
            "SCORES": {"LIMIT": 20},
        },
        "REQUESTS": {
            "MESSAGE": {
                "EMBED": {
                    "TITLE": "Служба поддержки 📟",
                    "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации, нажав на соответствующую кнопку ниже",
                    "COLOR": 0x2B2D31,
                },
                "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\nЖдите ответ от администрации, он будет отправлен вам в личные сообщения",
            },
            "CHANNELS": {
                "LOGS": None,
                "REMINDER": None,
            },
        },
        "NEAREST_EVENTS": {
            "CHANNEL": None,
            "CATEGORIES": ["Еженедельный ивент"],
        },
        "GAMES": {"CHANNELS": [], "ROULETTE": {"CHANCE": 60}},
        "SPECIAL": {
            "ROLES": {
                "1": {
                    "ROLES_HAVE": [
                        1056169412585066536,
                        1028040256903188530,
                        1056169408487247952,
                        1056169387872227370,
                        1071772832599650324,
                        785875027085492245,
                    ],
                    "ROLES_GET": [1056171848552939581],
                },
            },
            "EVENT_REWARDING": {
                "CHANNEL": 981593893567070298,
                "TIME": 10,
                "VOICES": [
                    858737175439736873,
                    1186721973242429480,
                    1046504818249846845,
                    1010586706677866626,
                ],
                "REWARDS": {
                    "everyone": {
                        "ROLES": ["everyone"],
                        "AMOUNT": 1,
                        "TITLE_UPDATED": False,
                        "ENABLED": True,
                    },
                },
            },
        },
        "ORDERS": {"CHANNEL": 829075875013591101, "ROLE": 829082636705595433},
        "BOOSTS_COUNTING": {
            "BOTS": {
                "DSMonitoring": 575776004233232386,
                "SD.C Monitoring": 464272403766444044,
            },
            "REMINDER": 478321260481478677,
        },
    },
    ###########################################################
    "COUNTERS": {
        "LOSE_SCORES": 0,
        "MESSAGES_PREVIOUS_BESTS": [
            891434928644968458,
            942161848768278571,
            960881081836503070,
        ],
        "BOOSTS": {
            "995006088959250623": 60,
            "885838857076097045": 11,
            "942161848768278571": 24,
            "960881081836503070": 3,
            "1184510335391109202": 2,
        },
        "ORDERS": 3,
        "ADDED_SCORES": 140,
        "REMOVED_SCORES": 57,
        "MAX_NUMBER_AT_EVENT": 0,
        "NUMBER_OF_EVENTS": 0,
        "TOTAL_SCORES": 0,
    },
}
# {
#     "GUILD_ID": 1189637072030531695,
#     "GENERAL": {
#         "PASSWORD": 111111,
#         "WELCOME": False,
#         "FAREWELL": False,
#         "MODERATION": {"GIF": False},
#         "AUTOUPDATE": {"MESSAGES": False, "SCORES": False},
#         "NEAREST_EVENTS": False,
#         "EXPERIENCE": False,
#         "GAMES": {"ALL_GAMES": False, "BLACKJACK": False, "ROULETTE": False},
#         "ORDERS": False,
#         "REQUESTS": False,
#         "SCORES": False,
#         "BOOSTS": False,
#         "REACTIONS_THREADS": False,
#         "ROLES": False,
#         "EVENT_REWARDING": False,
#     },
#     ###########################################################
#     "COGS": {
#         "WELCOME": {
#             "CHANNEL": None,
#             "EMBED": {
#                 "TITLE": "Добро пожаловать на сервер! 💌",
#                 "DESCRIPTION": "{member.mention}, приветствую тебя на сервере! 🌼",
#                 "IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
#                 "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
#                 "COLOR": 0x2B2D31,
#             },
#         },
#         "FAREWELL": {
#             "CHANNEL": None,
#             "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл с сервера!",
#         },
#         "REACTIONS_THREADS": {
#             "1189981495658565632": {
#                 "REACTIONS": ["<:23d4a3c46fea7f81:1193904492861718629>"],
#                 "THREAD": False,
#             },
#         },
#         "MODERATION": {"CHANNELS": [], "GIF": {"DELAY": 10}},
#         "SCORES": {
#             "REWARDS": [
#                 {"ROLE": 1198738747156615309, "AMOUNT": 8},
#                 {"ROLE": 1198738761186553959, "AMOUNT": 12},
#                 {"ROLE": 1198738770267218070, "AMOUNT": 18},
#             ],
#         },
#         "EXPERIENCE": {
#             "REWARDS": [
#                 {"ROLE": 1198738747156615309, "AMOUNT": 1},
#                 {"ROLE": 1198738761186553959, "AMOUNT": 5},
#                 {"ROLE": 1198738770267218070, "AMOUNT": 10},
#             ],
#         },
#         "AUTOUPDATE": {
#             "CHANNEL": None,
#             "MESSAGES": {"LIMIT": 10},
#             "SCORES": {"LIMIT": 20},
#         },
#         "REQUESTS": {
#             "MESSAGE": {
#                 "EMBED": {
#                     "TITLE": "Служба поддержки 📟",
#                     "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации, нажав на соответствующую кнопку ниже",
#                     "COLOR": 0x2B2D31,
#                 },
#                 "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\nЖдите ответ от администрации, он будет отправлен вам в личные сообщения",
#             },
#             "CHANNELS": {
#                 "LOGS": None,
#                 "REMINDER": None,
#             },
#         },
#         "NEAREST_EVENTS": {
#             "CHANNEL": None,
#             "CATEGORIES": ["Еженедельный ивент"],
#         },
#         "GAMES": {"CHANNELS": [], "ROULETTE": {"CHANCE": 60}},
#         "SPECIAL": {
#             "ROLES": [],
#             "EVENT_REWARDING": {
#                 "CHANNEL": 1189981495658565632,
#                 "TIME": 1,
#                 "VOICES": [
#                     1189637072487723081,
#                 ],
#                 "ROLES": [
#                     {"ROLES": [1198738761186553959], "AMOUNT": 123},
#                     {"ROLES": "everyone", "AMOUNT": 100},
#                 ],
#             },
#         },
#         "ORDERS": {"CHANNEL": 1189981495658565632, "ROLE": 1198738747156615309},
#         "BOOSTS_COUNTING": {
#             "BOTS": {
#                 "DSMonitoring": 575776004233232386,
#                 "SD.C Monitoring": 464272403766444044,
#             },
#             "REMINDER": 478321260481478677,
#         },
#     },
#     ###########################################################
#     "COUNTERS": {
#         "LOSE_SCORES": 0,
#         "MESSAGES_PREVIOUS_BESTS": [],
#         "BOOSTS": {},
#         "ORDERS": 3,
#         "ADDED_SCORES": 64,
#         "REMOVED_SCORES": 56,
#         "MAX_NUMBER_AT_EVENT": 0,
#         "NUMBER_OF_EVENTS": 0,
#         "TOTAL_SCORES": 0,
#     },
# },

dicts1 = {
    "GUILD_ID": 1189637072030531695,
    "GENERAL": {
        "PASSWORD": 111111,
        "WELCOME": False,
        "FAREWELL": False,
        "MODERATION": {"GIF": False},
        "AUTOUPDATE": {"MESSAGES": False, "SCORES": False},
        "NEAREST_EVENTS": False,
        "EXPERIENCE": False,
        "GAMES": {"ALL_GAMES": False, "BLACKJACK": False, "ROULETTE": False},
        "ORDERS": False,
        "REQUESTS": False,
        "SCORES": False,
        "BOOSTS_COUNTING": False,
        "REACTIONS_THREADS": False,
        "ROLES": False,
        "EVENT_REWARDING": False,
    },
    ###########################################################
    "COGS": {
        "WELCOME": {
            "CHANNEL": None,
            "EMBED": {
                "TITLE": "Добро пожаловать на сервер!  💌",
                "DESCRIPTION": "{member.mention}, рады тебя видеть на нашем сервере!\n",
                "IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
                "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
                "COLOR": 0x2B2D31,
            },
        },
        "FAREWELL": {
            "CHANNEL": None,
            "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл с сервера!",
        },
        "REACTIONS_THREADS": {},
        "MODERATION": {"CHANNELS": [], "GIF": {"DELAY": 10}},
        "SCORES": {
            "REWARDS": [],
        },
        "EXPERIENCE": {"REWARDS": []},
        "AUTOUPDATE": {
            "CHANNEL": None,
            "MESSAGES": {"LIMIT": 10},
            "SCORES": {"LIMIT": 20},
        },
        "REQUESTS": {
            "MESSAGE": {
                "EMBED": {
                    "TITLE": "Служба поддержки 📟",
                    "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации, нажав на соответствующую кнопку ниже",
                    "COLOR": 0x2B2D31,
                },
                "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\nЖдите ответ от администрации, он будет отправлен вам в личные сообщения",
            },
            "CHANNELS": {
                "LOGS": None,
                "REMINDER": None,
            },
        },
        "NEAREST_EVENTS": {
            "CHANNEL": None,
            "CATEGORIES": ["Еженедельный ивент"],
        },
        "GAMES": {"CHANNELS": [], "ROULETTE": {"CHANCE": 60}},
        "SPECIAL": {
            "ROLES": {},
            "EVENT_REWARDING": {
                "CHANNEL": None,
                "TIME": 10,
                "VOICES": [],
                "REWARDS": {
                    "everyone": {
                        "ROLES": ["everyone"],
                        "AMOUNT": 1,
                        "TITLE_UPDATED": False,
                        "ENABLED": True,
                    },
                },
            },
        },
        "ORDERS": {"CHANNEL": None, "ROLE": None},
        "BOOSTS_COUNTING": {
            "BOTS": {
                "DSMonitoring": 575776004233232386,
                "SD.C Monitoring": 464272403766444044,
            },
            "REMINDER": 478321260481478677,
        },
    },
    ###########################################################
    "COUNTERS": {
        "LOSE_SCORES": 0,
        "MESSAGES_PREVIOUS_BESTS": [],
        "BOOSTS": {},
        "ORDERS": 0,
        "ADDED_SCORES": 0,
        "REMOVED_SCORES": 0,
        "MAX_NUMBER_AT_EVENT": 0,
        "NUMBER_OF_EVENTS": 0,
        "TOTAL_SCORES": 0,
    },
}
