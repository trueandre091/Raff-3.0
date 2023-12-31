from os import getcwd
import disnake
from json import load, dump

FOLDER = getcwd()


async def count_orders_counter() -> None:
    """Сounting the number of orders"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["ORDERS"] += 1

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def count_failed_gif_counter() -> None:
    """Сounting the number of failed attempts to send"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["FAILED_GIF_TRY"] += 1

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def count_number_of_events_counter() -> None:
    """Сounting the number of events"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["NUMBER_OF_EVENTS"] += 1

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def count_lose_scores(scores: int):
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["LOSE_SCORES"] += scores

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def count_every_message(message: disnake.Message) -> None:
    """Counting every users' messages to database"""
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


async def count_users_boosts(author_id: int) -> None:
    """Counting users' boost on the monitoring sites"""
    with(open(f"{FOLDER}/data/counters.json", 'r', encoding='utf-8') as f):
        data = load(f)

    if str(author_id) not in data["BOOSTS"]:
        data["BOOSTS"][str(author_id)] = 1
    else:
        data["BOOSTS"][str(author_id)] += 1

    with(open(f"{FOLDER}/data/counters.json", 'w', encoding='utf-8') as f):
        dump(data, f)


async def count_added_scores(scores: int) -> None:
    """Counting added scores"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["ADDED_SCORES"] += scores

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)


async def count_removed_scores(scores: int) -> None:
    """Counting removed scores"""
    with (open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f):
        data = load(f)

    data["REMOVED_SCORES"] += scores

    with (open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f):
        dump(data, f)
