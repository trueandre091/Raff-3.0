from os import getcwd
import disnake
from disnake.ext import commands
from json import load, dump

FOLDER = getcwd()


def count_messages_to_data(author_id) -> None:
    """Counting every member's message"""
    with(open(f"{FOLDER}/data/lb_messages_data.json", 'r', encoding='utf-8') as f):
        data = load(f)

    if str(author_id) not in data:
        data[str(author_id)] = 1
    else:
        data[str(author_id)] += 1

    with(open(f"{FOLDER}/data/lb_messages_data.json", 'w', encoding='utf-8') as f):
        dump(data, f)


def count_orders_counter() -> None:
    """Сounting the number of orders"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["ORDERS"] += 1

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


def count_failed_gif_counter() -> None:
    """Сounting the number of failed attempts to send"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["FAILED_GIF_TRY"] += 1

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


def count_number_of_events_counter() -> None:
    """Сounting the number of events"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["NUMBER_OF_EVENTS"] += 1

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


def count_every_message(message) -> None:
    """Counting every users' messages to data base"""
    if not message.author.bot:
        author_id = message.author.id
        with(open(f"{FOLDER}/data/lb_messages_data.json", 'r', encoding='utf-8') as f):
            data = load(f)

        if str(author_id) not in data:
            data[str(author_id)] = 1
        else:
            data[str(author_id)] += 1

        with(open(f"{FOLDER}/data/lb_messages_data.json", 'w', encoding='utf-8') as f):
            dump(data, f)

def count_users_boosts(message) -> None:
    """Counting users' boost on the monitoring sites"""
    author_id = message.author.id
    with(open(f"{FOLDER}/data/counters.json", 'r', encoding='utf-8') as f):
        data = load(f)

    if str(author_id) not in data["BOOSTS"]:
        data["BOOSTS"][str(author_id)] = 1
    else:
        data["BOOSTS"][str(author_id)] += 1

    with(open(f"{FOLDER}/data/counters.json", 'w', encoding='utf-8') as f):
        dump(data, f)
