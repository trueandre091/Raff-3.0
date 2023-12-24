GUILD_CONFIG = {
    "TIMERS": {
        "CHANNEL": 785312596546813974,
        "MESSAGE": "По любым вопросам --> <#992788044514082876> <:B_andre2:1053723610197524530>",
    },
    "SETTINGS": {
        "AMOUNT_TO_FIRST_LVL": 8,
        "AMOUNT_TO_THIRD_LVL": 12,
        "AMOUNT_TO_FIFTH_LVL": 16,
        "CHANCE": 60,
        "MESSAGES_FOR_GIF": 15,
        "PASSWORD": 152364,
    },
    "WELCOME_SETTINGS": {
        "CHANNEL": 785312596059226114,
        "EMBED": {
            # возможно использование переменных: {member.mention}, {member}
            "TITLE": "Добро пожаловать на Homey Temple!  💌",
            # возможно использование переменных: {member.mention}, {member}
            "DESCRIPTION": "{member.mention}, рады тебя видеть!\nПриходи на ближайшие мероприятия, если будет время <#1160687361269694505> 🌼",
            "COLOR": 0x2B2D31,
        },
        "AVATAR_IF_ERROR": "https://im.wampi.ru/2023/11/02/Bez_nazvania1_20211210115049.png",
        "BACKGROUND_IMAGE": "https://i.postimg.cc/25znZVnG/DALLE-2023-02-22-19-01-33-a-spring-flowery-background-1.png",
    },
    "FAREWELL_SETTINGS": {
        "CHANNEL": 785313517481099274,
        # возможно использование переменных: {member.mention}, {member.nick}, {member.name}, {member}
        "MESSAGE": "{member.mention} / {member.name} / {member.nick} ушёл.",
    },
    "ADDING_REACTIONS_THREADS_SETTINGS": {
        "858731672677515294": {"REACTIONS": [], "THREAD": None},
        "785312596546813976": {
            "REACTIONS": ["<:B_00like:1001544330613375026>", "<:B_00likenot:1001544295532204082>"],
            "THREAD": True,
        },
        "1160687361269694505": {
            "REACTIONS": ["<:B_00like:1001544330613375026>", "<:B_00likenot:1001544295532204082>", "✅"],
            "THREAD": False,
        },
    },
    "MODERATION_SETTINGS": {"GIF": {"MESSAGES_FOR_GIF": 15}},
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
                "BOOSTS": {
                    "ROLES_HAVE": [
                        1056169412585066536,
                        1028040256903188530,
                        1056169408487247952,
                        1056169387872227370,
                        1071772832599650324,
                        785875027085492245,
                    ],
                    "ROLES_GET": [1056171848552939581],
                }
            },
            "EVENTS": {
                "TIME": 1860,
                "CHANNELS": [858737175439736873, 1186721973242429480, 1046504818249846845, 1010586706677866626],
                "SCORES": 1,
            },
        },
        "SCORES": {
            "AMOUNT_TO_FIRST_LVL": 8,
            "AMOUNT_TO_THIRD_LVL": 12,
            "AMOUNT_TO_FIFTH_LVL": 20,
        },
        "GAMES": {"ROULETTE": {"CHANCE": 60}},
        "AUTOUPDATE": {
            "MESSAGES": {"PLACE_LIMIT": 10},
            "SCORES": {},
            "CHANNEL": 994881716307116073,
        },
        "EVENTS": {"CHANNEL": 1160687361269694505},
        "ORDERS": {"CHANNEL": 829075875013591101, "BARMEN_ROLE": 829082636705595433},
        "REQUESTS": {
            "BUTTONS_MESSAGE": {
                "CHANNEL": 992788044514082876,
                "EMBED": {
                    "TITLE": "Служба поддержки 📟",
                    "DESCRIPTION": "При помощи кнопок к сообщению вы можете сделать запрос по любому поводу у администрации и оставить отзыв о качестве поддержки, нажав на соответствующие кнопки ниже",
                    "COLOR": 0x2B2D31,
                },
                "CALLBACK": "Запрос успешно отправлен! <a:A_heart1:993383076363239444>\n`Ждите ответ от администрации, он будет отправлен вам в личные сообщения`",
            },
            "LOGS_MESSAGE": {"CHANNEL": 981593893567070298},
        },
        "EXPERIENCE": {"FACTOR": 5},
    },
}
