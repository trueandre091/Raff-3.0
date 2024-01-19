GUILD_CONFIG = {
    "GUILD_ID": None,
    "TIMERS": {
        "CHANNEL": None,
        "MESSAGE": "Таймер",
    },
    "GENERAL_SETTINGS": {
        "PASSWORD": 111111,
        "WELCOME": False,
        "FAREWELL": False,
        "MODERATION": {"GIF": False},
        "AUTOUPDATE_MESSAGES": {"MESSAGES": False, "SCORES": False},
        "NEAREST_EVENTS": False,
        "EXPERIENCE": False,
        "GAMES": {"ALL_GAMES": False, "BLACKJACK": False, "ROULETTE": False},
        "ORDERS": False,
        "REQUESTS": False,
        "SCORES": False,
        "COUNTING_BOOSTS": False,
        "ADDING_REACTIONS_THREADS": False,
        "AUTO_ADDING_ROLES": False,
        "AUTO_ADDING_SCORES_FOR_TIME_IN_VOICE_CHANNEL": False,
    },
    "WELCOME_SETTINGS": {
        "CHANNEL": None,
        "EMBED": {
            # возможно использование переменных: {member.mention}, {member}
            "TITLE": "Добро пожаловать на сервер!  💌",
            # возможно использование переменных: {member.mention}, {member}
            "DESCRIPTION": "{member.mention}, рады тебя видеть!\nПриходи на ближайшие мероприятия, если будет время <#1160687361269694505> 🌼",
            "COLOR": 0x2B2D31,
        },
        "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
        "BACKGROUND_IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
    },
    "FAREWELL_SETTINGS": {
        "CHANNEL": None,
        # возможно использование переменных: {member.mention}, {member.nick}, {member.name}, {member}
        "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл.",
    },
    "ADDING_REACTIONS_THREADS_SETTINGS": {
        # None: {"REACTIONS": [], "THREAD": False},
    },
    "MODERATION_SETTINGS": {"CHANNEL": [None], "GIF": {"MESSAGES_FOR_GIF": 10}},
    "BOOSTS_COUNTING_SETTINGS": {
        "BOOST_BOTS": {
            "DSMonitoring": 575776004233232386,
            "SD.C Monitoring": 464272403766444044,
        },
        "REMINDER": 478321260481478677,
    },
    "COGS_SETTINGS": {
        "SPECIAL": {
            "ROLES": {
                # "BOOSTS": {
                #     "ROLES_HAVE": [None],
                #     "ROLES_GET": [None],
                # }
            },
            "EVENTS": {
                "TIME": 10,
                "CHANNELS": [None],
                "ADMIN_CHANNEL": None,
                "ROLES": [
                    {"ROLES_ID": [None], "SCORES": None},
                    {"ROLES_ID": "everyone", "SCORES": 1},
                ],
            },
        },
        "SCORES": {
            "AMOUNT_TO_FIRST_LVL": 8,
            "AMOUNT_TO_THIRD_LVL": 12,
            "AMOUNT_TO_FIFTH_LVL": 16,
        },
        "GAMES": {"CHANNELS": [None], "ROULETTE": {"CHANCE": 60}},
        "AUTOUPDATE": {
            "MESSAGES": {"PLACE_LIMIT": 10},
            "SCORES": {"PLACE_LIMIT": 20},
            "CHANNEL": None,
        },
        "NEAREST_EVENTS": {
            "CHANNEL": None,
            "CATEGORIES": ["Еженедельный ивент", "Особый ивент"],
        },
        "ORDERS": {"CHANNEL": None, "BARMEN_ROLE": None},
        "REQUESTS": {
            "BUTTONS_MESSAGE": {
                "EMBED": {
                    "TITLE": "Служба поддержки 📟",
                    "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации, нажав на соответствующую кнопку ниже",
                    "COLOR": 0x2B2D31,
                },
                "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\n`Ждите ответ от администрации, он будет отправлен вам в личные сообщения`",
                "CHANNEL": None,
            },
            "LOGS_MESSAGE": {"CHANNEL": None},
            "ADMIN_CHANNEL": None,
        },
        "EXPERIENCE": {"FACTOR": 5, "LEVELING": [{"ROLE_ID": None, "AMOUNT": None}]},
    },
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
