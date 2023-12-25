GUILD_CONFIG = {
    "TIMERS": {
        "CHANNEL": None,
        "MESSAGE": "Таймер",
    },
    "GENERAL_SETTINGS": {
        "PASSWORD": 111111,
        "WELCOME": False,
        "FAREWELL": False,
        "MODERATION": {"GIF": False},
        "AUTOUPDATE_MESSAGES": False,
        "NEAREST_EVENTS": False,
        "EXPERIENCE": False,
        "GAMES": {"BLACKJACK": False, "ROULETTE": False},
        "ORDERS": False,
        "REQUESTS": False,
        "SCORES": False,
        "COUNTING_BOOSTS": False,
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
    "MODERATION_SETTINGS": {"GIF": {"MESSAGES_FOR_GIF": 10}},
    "BOOSTS_COUNTING_SETTINGS": {
        "BOOST_BOTS": {"DSMonitoring": 575776004233232386, "SD.C Monitoring": 464272403766444044},
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
                "TIME": 1860,
                "CHANNELS": [None],
                "SCORES": 1,
            },
        },
        "SCORES": {
            "AMOUNT_TO_FIRST_LVL": 8,
            "AMOUNT_TO_THIRD_LVL": 12,
            "AMOUNT_TO_FIFTH_LVL": 16,
        },
        "GAMES": {"ROULETTE": {"CHANCE": 60}, "BLACKJACK": True},
        "AUTOUPDATE": {
            "MESSAGES": {"PLACE_LIMIT": 10},
            "SCORES": {},
            "CHANNEL": None,
        },
        "EVENTS": {"CHANNEL": None, "CATEGORIES": ["Еженедельный ивент", "Особый ивент"]},
        "ORDERS": {"CHANNEL": None, "BARMEN_ROLE": None},
        "REQUESTS": {
            "BUTTONS_MESSAGE": {
                "CHANNEL": None,
                "EMBED": {
                    "TITLE": "Служба поддержки 📟",
                    "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации и оставить отзыв о качестве поддержки, нажав на соответствующие кнопки ниже",
                    "COLOR": 0x2B2D31,
                },
                "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\n`Ждите ответ от администрации, он будет отправлен вам в личные сообщения`",
            },
            "LOGS_MESSAGE": {"CHANNEL": None},
            "ADMIN_CHANNEL": None,
        },
        "EXPERIENCE": {"FACTOR": 5},
    },
}
