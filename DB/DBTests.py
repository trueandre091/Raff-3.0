from loguru import logger
import asyncio
from sqlalchemy import create_engine
from DB.models import Base
from DB.JSONEnc import JsonEncoder
from DB.DataBase import UserDBase, GuildsDBase, RelationshipsDBase

logger.add(
    "DBTestslogs.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
    level="INFO",
    rotation="1 week",
    compression="zip",
    backtrace=True,
    diagnose=True,
)


####################################   USERS TESTS   ############################################


async def test_add_user(users_echo=False):
    db = UserDBase(users_echo)

    data = {"username": "TopNik_", "ds_id": 785364734786, "scores": 20}

    await db.add_user(data)


async def test_add_some_users(users_echo=False):
    db = UserDBase(users_echo)

    data = [
        {"username": "Andre", "ds_id": 674325879834},
        {"username": "Minion", "ds_id": 977865342843},
    ]

    await db.add_user(data)


async def test_get_user(users_echo=False):
    db = UserDBase(users_echo)

    data = {"ds_id": 785364734786}

    await db.get_user(data)


async def test_get_some_users(users_echo=False):
    db = UserDBase(users_echo)

    data = [{"ds_id": 674325879834}, {"ds_id": 977865342843}]

    await db.get_user(data)


async def test_get_user_with_guilds(users_echo=False):
    db = UserDBase(users_echo)

    data = {"ds_id": 529291000418402314}

    res = await db.get_user_with_guilds(data)

    logger.debug(res.guilds)


async def test_get_some_users_with_guilds(users_echo=False):
    db = UserDBase(users_echo)

    data = [{"ds_id": 520600815535128587}, {"ds_id": 529291000418402314}]

    res = await db.get_user_with_guilds(data)

    for user in res:
        logger.debug(user.guilds)


async def test_get_all_users(users_echo=False):
    db = UserDBase(users_echo)

    res = await db.get_all_users()

    logger.debug(res)


async def test_get_all_users_with_guilds(users_echo=False):
    db = UserDBase(users_echo)

    res = await db.get_all_users_with_guilds()

    for user in res:
        logger.debug(user, user.guilds, sep="-------")


async def test_update_user(users_echo=False):
    db = UserDBase(users_echo)

    data = {"ds_id": 674325879834, "scores": 10}

    await db.update_user(data)


async def test_update_some_users(users_echo=False):
    db = UserDBase(users_echo)

    data = [
        {"ds_id": 674325879834, "username": "андре", "scores": 15},
        {"ds_id": 977865342843, "experience": 1_000},
    ]

    await db.update_user(data)


async def test_get_top_users_by_scores(users_echo=False):
    db = UserDBase(users_echo)

    res = await db.get_top_users_by_scores()

    logger.debug(res)

    ####################################   GUILDS TESTS   ############################################


async def test_add_guild(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    data = {"guild_id": 785312593614209055, "guild_name": "Homey Temple"}

    await db.add_guild(data)


async def test_add_some_guilds(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    data = [
        {"guild_id": 785312593614209055, "guild_name": "Homey Temple"},
        {"guild_id": 710525764470308975, "guild_name": "NetherWorld"},
    ]

    await db.add_guild(data)


async def test_get_guild(guilds_echo=False):
    db = GuildsDBase(guilds_echo)
    enc = JsonEncoder()

    data = {"guild_id": 1189637072030531695}

    res = await db.get_guild(data)
    logger.debug(type(res.guild_sets))

    sets = enc.code_from_json(res.guild_sets)
    logger.debug(type(sets), sets, sep="\n")


async def test_get_guild_with_users(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    data = {"guild_id": 785312593614209055}

    res = await db.get_guild_with_users(data)

    logger.debug(res.users)


async def test_get_some_guilds(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    data = [{"guild_id": 710525764470308975}, {"guild_id": 785312593614209055}]

    await db.get_guild(data)


async def test_get_all_guilds(guilds_echo):
    db = GuildsDBase(guilds_echo)

    res = await db.get_all_guilds()

    logger.debug(res)


async def test_get_all_guilds_with_users(guilds_echo):
    db = GuildsDBase(guilds_echo)

    res = await db.get_all_guilds_with_users()

    for guild in res:
        logger.debug(str(guild) + "-------" + str(guild.users))


async def test_update_guild(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    data = {"guild_id": 710525764470308975, "guild_name": "NetWorld"}

    await db.update_guild(data)


async def test_update_some_guilds(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    data = [
        {"guild_id": 710525764470308975, "count_members": 5000},
        {"guild_id": 785312593614209055, "count_members": 100},
    ]

    await db.update_guild(data)


async def test_guild_get_top_users_by_scores(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    res = await db.get_top_users_by_scores(785312593614209055)

    for user in res:
        logger.debug(str(user) + str(user.scores))


async def test_guild_get_top_users_by_messages(guilds_echo=False):
    db = GuildsDBase(guilds_echo)

    res = await db.get_top_users_by_messages(785312593614209055)

    for user in res:
        logger.debug(str(user) + str(user.messages))


async def test_get_sets(guilds_echo):
    db = GuildsDBase(guilds_echo)
    enc = JsonEncoder()

    res = await db.get_guild({"guild_id": 1189637072030531695})

    if res:
        sets = enc.code_from_json(res.guild_sets)
        logger.debug(sets)

    ####################################   RELATIONSHIPS TESTS   ############################################


async def test_add_all_relationships_in_one_time(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    # HOMEY TEMPLE DATA
    users_hom_tem = [{"ds_id": 785364734786}, {"ds_id": 674325879834}]

    guild_hom_tem = [{"guild_id": 785312593614209055}]

    data_hom_tem = {"users": users_hom_tem, "guilds": guild_hom_tem}

    # NETHERWORLD DATA
    users_net_world = [{"ds_id": 785364734786}, {"ds_id": 977865342843}]

    guild_net_world = [{"guild_id": 710525764470308975}]

    data_net_world = {"users": users_net_world, "guilds": guild_net_world}

    data = [data_hom_tem, data_net_world]

    await db.add_relationship(data)


async def test_add_relationship_for_HomTem(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    users = [{"ds_id": 785364734786}, {"ds_id": 674325879834}]

    guild = [{"guild_id": 785312593614209055}]

    data = {"users": users, "guilds": guild}

    await db.add_relationship(data)


async def test_add_relationship_for_NetWorld(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    users = [{"ds_id": 785364734786}, {"ds_id": 977865342843}]

    guild = [{"guild_id": 710525764470308975}]

    data = {"users": users, "guilds": guild}

    await db.add_relationship(data)


async def test_delete_relationship(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    user = [{"ds_id": 785364734786}]
    guild = [{"guild_id": 785312593614209055}]

    data = {"users": user, "guilds": guild}

    await db.delete_relationship(data)

    ####################################   DATABASE TESTS   ############################################


async def main():
    users_echo = False

    # USERS TESTS
    # await test_add_user(users_echo)
    # await test_add_some_users(users_echo)

    # await test_get_user(users_echo)
    # await test_get_some_users(users_echo)

    # await test_get_user_with_guilds(users_echo)
    # await test_get_some_users_with_guilds(users_echo)

    # await test_get_all_users(users_echo)
    # await test_get_all_users_with_guilds(users_echo)

    # await test_update_user(users_echo)
    # await test_update_some_users(users_echo)

    # await test_get_top_users_by_scores(users_echo)

    ###################################################

    guilds_echo = False

    # GUILDS TESTS
    # await test_add_guild(guilds_echo)
    # await test_add_some_guilds(guilds_echo)

    # await test_get_guild(guilds_echo)
    # await test_get_some_guilds(guilds_echo)

    # await test_get_all_guilds(guilds_echo)
    # await test_get_all_guilds_with_users(guilds_echo)

    # await test_update_guild(guilds_echo)
    # await test_update_some_guilds(guilds_echo)

    # await test_guild_get_top_users_by_scores(guilds_echo)
    # await test_guild_get_top_users_by_messages(guilds_echo)

    await test_get_sets(guilds_echo)

    ###################################################

    rel_echo = True

    # RELATIONSHIPS TESTS

    # await test_add_all_relationships_in_one_time(rel_echo)

    # await test_add_relationship_for_HomTem(rel_echo)
    # await test_add_relationship_for_NetWorld(rel_echo)
    # await asyncio.sleep(2)
    # await test_get_user_with_guilds(rel_echo)
    # await test_get_guild_with_users(rel_echo)

    # await test_delete_relationship(rel_echo)


if __name__ == "__main__":
    # echo = False
    # engine = create_engine("sqlite:///DataBase.db", echo=echo)
    # Base.metadata.create_all(engine)
    # engine.echo = True

    asyncio.run(main())
