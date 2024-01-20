from os import getcwd
import disnake
from json import load, dump
from cogs.cog_guilds_functions import DB, GDB, guild_sets_check

FOLDER = getcwd()


async def count_orders_counter(guild_id: int) -> None:
    """Counting the number of orders"""
    settings = await guild_sets_check(guild_id)
    settings["COUNTERS"]["ORDERS"] += 1

    await GDB.update_guild(guild_id=guild_id, guild_sets=settings)


async def count_failed_gif_counter() -> None:
    """Counting the number of failed attempts to send"""
    with open(f"{FOLDER}/data/counters.json", "r", encoding="utf-8") as f:
        data = load(f)

    data["FAILED_GIF_TRY"] += 1

    with open(f"{FOLDER}/data/counters.json", "w", encoding="utf-8") as f:
        dump(data, f)


async def count_number_of_events_counter(guild_id: int) -> None:
    """Counting the number of events"""
    settings = await guild_sets_check(guild_id)
    settings["COUNTERS"]["NUMBER_OF_EVENTS"] += 1

    await GDB.update_guild(guild_id=guild_id, guild_sets=settings)


async def count_lose_scores(scores: int, guild_id: int):
    settings = await guild_sets_check(guild_id)
    settings["COUNTERS"]["LOSE_SCORES"] += scores

    await GDB.update_guild(guild_id=guild_id, guild_sets=settings)


async def count_every_message(message: disnake.Message) -> None:
    """Counting every users' messages to database"""
    if not message.author.bot:
        author_id = message.author.id
        user = await DB.get_user(ds_id=author_id)
        if user is None:
            await DB.add_user(ds_id=author_id, username=message.author.name, messages=1)
        else:
            await DB.update_user(
                ds_id=author_id,
                username=message.author.name,
                messages=user.messages + 1,
            )


async def count_users_boosts(author_id: int, guild_id: int) -> None:
    """Counting users' boost on the monitoring sites"""
    settings = await guild_sets_check(guild_id)
    if str(author_id) in settings["COUNTERS"]["BOOSTS"]:
        settings["COUNTERS"]["BOOSTS"][str(author_id)] += 1
    else:
        settings["COUNTERS"]["BOOSTS"][str(author_id)] = 1

    await GDB.update_guild(guild_id=guild_id, guild_sets=settings)


async def count_added_scores(scores: int, guild_id: int) -> None:
    """Counting added scores"""
    settings = await guild_sets_check(guild_id)
    settings["COUNTERS"]["ADDED_SCORES"] += scores

    await GDB.update_guild(guild_id=guild_id, guild_sets=settings)


async def count_removed_scores(scores: int, guild_id: int) -> None:
    """Counting removed scores"""
    settings = await guild_sets_check(guild_id)
    settings["COUNTERS"]["REMOVED_SCORES"] += scores

    await GDB.update_guild(guild_id=guild_id, guild_sets=settings)
