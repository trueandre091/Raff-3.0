GUILD_CONFIG = {
    "GUILD_ID": None,
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
        "BOOSTS": False,
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
                "BACKGROUND_IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
                "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
                "COLOR": 0x2B2D31,
            },
        },
        "FAREWELL": {
            "CHANNEL": None,
            "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл с сервера!",
        },
        "REACTIONS_THREADS": {
            # None: {"REACTIONS": [], "THREAD": False},
        },
        "MODERATION": {"CHANNELS": [], "GIF": {"DELAY": 10}},
        "SCORES": {
            "REWARDS": [
                # {"ROLE": None, "AMOUNT": None}
            ],
        },
        "EXPERIENCE": {
            "REWARDS": [
                # {"ROLE": None, "AMOUNT": None}
            ],
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
                # "BOOSTS": {
                #     "ROLES_HAVE": [None],
                #     "ROLES_GET": [None],
                # }
            },
            "EVENT_REWARDING": {
                "CHANNEL": None,
                "TIME": 10,
                "VOICES": [],
                "ROLES": [
                    # {"ROLES": [], "SCORES": None},
                    {"ROLES": "everyone", "SCORES": 1},
                ],
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
