import asyncio
from sqlalchemy import create_engine
from DB.models import Base
from DataBase import UserDBase, GuildsDbase, RelationshipsDBase


####################################   USERS TESTS   ############################################


async def test_add_user(users_echo=False):
    db = UserDBase(users_echo)

    data = {"username": "TopNik_",
            "ds_id": 785364734786,
            "scores": 20}

    await db.add_user(data)


async def test_add_some_users(users_echo=False):
    db = UserDBase(users_echo)

    data = [{"username": "Andre",
             "ds_id": 674325879834},
            {"username": "Minion",
             "ds_id": 977865342843}]

    await db.add_user(data)


async def test_get_user(users_echo=False):
    db = UserDBase(users_echo)

    data = {"ds_id": 785364734786}

    await db.get_user(data)


async def test_get_some_users(users_echo=False):
    db = UserDBase(users_echo)

    data = [{"ds_id": 674325879834},
            {"ds_id": 977865342843}]

    await db.get_user(data)


async def test_get_user_with_guilds(users_echo=False):
    db = UserDBase(users_echo)

    data = {"ds_id": 785364734786}

    res = await db.get_user_with_guilds(data)

    print(res.guilds)


async def test_get_some_users_with_guilds(users_echo=False):
    db = UserDBase(users_echo)

    data = [{"ds_id": 674325879834},
            {"ds_id": 977865342843}]

    res = await db.get_user_with_guilds(data)

    for user in res:
        print(user.guilds)


async def test_update_user(users_echo=False):
    db = UserDBase(users_echo)

    data = {"ds_id": 674325879834,
            "scores": 10}

    await db.update_user(data)


async def test_update_some_users(users_echo=False):
    db = UserDBase(users_echo)

    data = [{"ds_id": 674325879834,
             "username": "андре",
             "scores": 10_000},
            {"ds_id": 977865342843,
             "experience": 1_000}]

    await db.update_user(data)


async def test_get_top_users_by_scores(users_echo=False):
    db = UserDBase(users_echo)

    res = await db.get_top_users_by_scores()

    print(res)

    ####################################   GUILDS TESTS   ############################################


async def test_add_guild(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = {"guild_id": 785312593614209055,
            "guild_name": "Homey Temple"}

    await db.add_guild(data)


async def test_add_some_guilds(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = [{"guild_id": 710525764470308975,
             "guild_name": "NetherWorld"}]

    await db.add_guild(data)


async def test_get_guild(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = {"guild_id": 710525764470308975}

    await db.get_guild(data)


async def test_get_guild_with_users(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = {"guild_id": 785312593614209055}

    res = await db.get_guild_with_users(data)

    print(res.users)


async def test_get_some_guilds(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = [{"guild_id": 710525764470308975},
            {"guild_id": 785312593614209055}]

    await db.get_guild(data)


async def test_update_guild(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = {"guild_id": 710525764470308975,
            "guild_name": "NetWorld"}

    await db.update_guild(data)


async def test_update_some_guilds(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    data = [{"guild_id": 710525764470308975,
             "count_members": 5000},
            {"guild_id": 785312593614209055,
             "count_members": 100}]

    await db.update_guild(data)


async def test_guild_get_top_users_by_scores(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    await db.get_top_users_by_scores(785312593614209055)

    ####################################   RELATIONSHIPS TESTS   ############################################


async def test_add_relationship_for_HomTem(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    users = [{"ds_id": 785364734786},
             {"ds_id": 674325879834}]

    guild = [{"guild_id": 785312593614209055}]

    data = {"users": users,
            "guilds": guild}

    await db.add_relationship(data)


async def test_add_relationship_for_NetWorld(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    users = [{"ds_id": 785364734786},
             {"ds_id": 977865342843}]

    guild = [{"guild_id": 710525764470308975}]

    data = {"users": users,
            "guilds": guild}

    await db.add_relationship(data)

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

    # await test_update_guild(guilds_echo)
    # await test_update_some_guilds(guilds_echo)

    # await test_guild_get_top_users_by_scores(guilds_echo)

    ###################################################

    rel_echo = False

    # RELATIONSHIPS TESTS
    # await test_add_relationship_for_HomTem(rel_echo)
    await test_add_relationship_for_NetWorld(rel_echo)
    # await asyncio.sleep(2)
    # await test_get_user_with_guilds(rel_echo)
    # await test_get_guild_with_users(rel_echo)


if __name__ == "__main__":
    # echo = False
    # engine = create_engine("sqlite:///DataBase.db", echo=echo)
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    # engine.echo = True

    asyncio.run(main())
