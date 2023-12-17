"""Database Management"""

import asyncio
from typing import Union, Any
import traceback

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload

from DB.models import Users, Guilds, Base


class DataBase:
    """Class for creating connection to database and managing it"""

    def __init__(self, echo_mode: bool = False):
        try:
            self.echo = echo_mode
            self.engine = create_engine("sqlite:///DB/DataBase.db", echo=self.echo)
            self.Session = sessionmaker(self.engine)
        except Exception:
            print(traceback.format_exc())
            raise "Error creating an engine or connecting to database"

    ####################################   USERS   ############################################


class UserDBase(DataBase):
    async def add_user(self, data: Union[dict, list[dict]]) -> Union[Users, list[Users], None]:
        """
        Adds a user to the database

        Accepts a dictionary or a list of dictionaries like:
        {"username": str,
        "ds_id": int}   (ds_id is unique identifier of discord)

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """
        default_scores = 10

        user_list = []
        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            try:
                for data in data:
                    user = Users(username=data["username"], ds_id=data["ds_id"],
                                 scores=data["scores"] if data.get("scores") else default_scores,
                                 experience=data["experience"] if data.get("experience") else 0)
                    user_list.append(user)
                    print(user)

                session.add_all(user_list)
                session.commit()

                return user_list[0] if is_dict else user_list
            except Exception:
                print("Something went wrong then adding user")
                print(traceback.format_exc())

        return

    @staticmethod
    def get_user_static(session, data):
        """
        A static method that gets user from database
        Called from others async functions

        Accepts session and data.
        Data have to have at least one parameter: ds_id or username.

        Attention:
        Search by ds_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        is_dict = True if type(data) == dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:
                if type(data) == list:
                    for ds_id in data:
                        user = (select(Users)
                                .filter_by(ds_id=ds_id))

                        user = session.scalars(user).first()
                        if not user:
                            print("Something went wrong when get user for relationship")
                            return

                        user_list.append(user)

                else:

                    if "ds_id" in data.keys():
                        user = (select(Users)
                                .filter_by(ds_id=data["ds_id"]))
                        user = session.scalars(user).first()
                        if not user:
                            print("Can't find user by discord id in database")
                            return

                        user_list.append(user)

                    elif "username" in data.keys():
                        user = (select(Users)
                                .filter_by(username=data["username"]))
                        user = session.scalars(user).first()
                        if not user:
                            print("Can't find user by username in database")
                            return

                        user_list.append(user)

                    return user_list[0] if is_dict else user_list

        except Exception:
            print("Something went wrong when get user")
            print(traceback.format_exc())

        return

    @staticmethod
    def get_user_static_with_guilds(session, data):
        """
        A static method that gets the user from the database with the guilds in which he belongs.
        Use selectinload parameter for query
        Called from others async functions

        Accepts session and data.
        Data have to have at least one parameter: ds_id or username.

        Attention:
        Search by ds_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        is_dict = True if type(data) == dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:
                if type(data) == list:
                    for ds_id in data:
                        user = (select(Users)
                                .options(Users.guilds)
                                .filter_by(ds_id=ds_id))

                        user = session.scalars(user).first()
                        if not user:
                            print("Something went wrong when get user for relationship")
                            return

                        user_list.append(user)

                else:
                    if "ds_id" in data.keys():
                        user = (select(Users)
                                .options(selectinload(Users.guilds))
                                .filter_by(ds_id=data["ds_id"]))
                        user = session.scalars(user).first()
                        if not user:
                            print("Can't find user by discord id in database")
                            return

                        user_list.append(user)

                    elif "username" in data.keys():
                        user = (select(Users)
                                .options(selectinload(Users.guilds))
                                .filter_by(username=data["username"]))
                        user = session.scalars(user).first()
                        if not user:
                            print("Can't find user by username in database")
                            return

                        user_list.append(user)

            return user_list[0] if is_dict else user_list

        except Exception:
            print("Something went wrong when get user")
            print(traceback.format_exc())

        return

    async def get_user(self, data: Union[dict, list[dict]]) -> Union[Users, list[Users], None]:
        """
        Gets user with get_user_static method from database
        get_user_static is a staticmethod

        Accepts data.
        Data have to have at least one parameter: ds_id or username.

        Attention:
        Search by ds_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        with self.Session() as session:
            user = self.get_user_static(session, data)
            if user:
                print(user)

            return user

    async def get_user_with_guilds(self, data: Union[dict, list[dict]]) -> Union[Users, list[Users], None]:
        """
        Method that gets the user from the database with the guilds in which he belongs
        get_user_static_with_guilds is a staticmethod

        Accepts data.
        Data have to have at least one parameter: ds_id or username.

        Attention:
        Search by ds_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        with self.Session() as session:
            user = self.get_user_static_with_guilds(session, data)
            if user:
                print(user)

            return user

    async def update_user(self, data: Union[dict, list[dict]]) -> Union[Users, list[Users], None]:
        """
        Updates user from database. Use get_user_static for getting user.

        Accepts data.
        Data have to have at least one parameter: ds_id or username

        Attention:
        Search by ds_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            users = self.get_user_static(session, data)
            try:
                for data in data:
                    for user in users:
                        if data["ds_id"] == user.ds_id:
                            user.username = user.username if data.get("username") is None else data["username"]
                            user.scores = user.scores if data.get("scores") is None else data["scores"]
                            user.experience = user.experience if data.get("experience") is None else data["experience"]

                session.commit()

                print(users)
                return users

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

    async def get_top_users_by_scores(self) -> Union[list, None]:
        with self.Session() as session:
            try:
                users = (select(Users)
                         .order_by(Users.scores.desc())
                         .limit(20))
                res = session.scalars(users).all()
                if not res:
                    print("Can't get top users by scores")
                    return

                return res

            except Exception:
                print("Something went wrong when get top for users by scores")
                print(traceback.format_exc())

        return

    ####################################   GUILDS   ############################################


class GuildsDbase(DataBase):
    async def add_guild(self, data: Union[dict, list[dict]]) -> Union[Guilds, list[Guilds], None]:

        guilds_list = []
        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            try:
                for data in data:
                    guild = Guilds(guild_id=data["guild_id"], guild_name=data["guild_name"],
                                   count_members=(data["count_members"] if data.get("count_members") else 0))
                    guilds_list.append(guild)

                session.add_all(guilds_list)
                session.commit()

                return guilds_list[0] if is_dict else guilds_list

            except Exception:
                print("Something went wrong then adding guild")
                print(traceback.format_exc())

        return

    @staticmethod
    def get_guild_static(session, data):

        guild_list = []
        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        try:
            for data in data:

                if type(data) == list:
                    for guild_id in data:
                        guild = (select(Guilds)
                                 .filter_by(guild_id=guild_id))

                        guild = session.scalars(guild).first()
                        if not guild:
                            print("Something went wrong when get guild for relationship")
                            return

                        guild_list.append(guild)

                if "guild_id" in data.keys():
                    guild = select(Guilds).filter_by(guild_id=data["guild_id"])
                    guild = session.scalars(guild).first()
                    if not guild:
                        print("Can't find guild by discord id in database")
                        return

                    guild_list.append(guild)

                elif "guild_name" in data.keys():
                    guild = select(Guilds).filter_by(guild_name=data["guild_name"])
                    guild = session.scalars(guild).first()
                    if not guild:
                        print("Can't find guild by guild name in database")
                        return

                    guild_list.append(guild)

            return guild_list[0] if is_dict else guild_list

        except Exception:
            print("Something went wrong when get guild")
            print(traceback.format_exc())

        return

    @staticmethod
    def get_guild_static_with_users(session, data):

        guild_list = []
        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        try:
            for data in data:

                if type(data) == list:
                    for guild_id in data:
                        guild = (select(Guilds)
                                 .options(selectinload(Guilds.users))
                                 .filter_by(guild_id=guild_id))

                        guild = session.scalars(guild).first()
                        if not guild:
                            print("Something went wrong when get guild for relationship")
                            return

                        guild_list.append(guild)

                else:

                    if "guild_id" in data.keys():
                        guild = (
                            select(Guilds).options(selectinload(Guilds.users)).filter_by(guild_id=data["guild_id"]))
                        guild = session.scalars(guild).first()
                        if not guild:
                            print("Can't find guild by discord id in database")
                            return

                        guild_list.append(guild)

                    elif "guild_name" in data.keys():
                        guild = (
                            select(Guilds).options(selectinload(Guilds.users)).filter_by(guild_name=data["guild_name"]))
                        guild = session.scalars(guild).first()
                        if not guild:
                            print("Can't find guild by guild name in database")
                            return

                        guild_list.append(guild)

            return guild_list[0] if is_dict else guild_list

        except Exception:
            print("Something went wrong when get guild")
            print(traceback.format_exc())

        return

    async def get_guild(self, data: Union[dict, list[dict]]) -> Union[Guilds, list[Guilds], None]:
        with self.Session() as session:
            return self.get_guild_static(session, data)

    async def get_guild_with_users(self, data: Union[dict, list[dict]]) -> Union[Guilds, list[Guilds], None]:
        with self.Session() as session:
            return self.get_guild_static_with_users(session, data)

    async def update_guild(self, data: Union[dict, list[dict]]) -> Union[Guilds, list[Guilds], None]:

        guilds_list = []
        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            guilds = self.get_guild_static(session, data)
            try:
                for data in data:
                    for guild in guilds:
                        if data["guild_id"] == guild.guild_id:
                            guild.guild_name = guild.guild_name if data.get("guild_name") is None else data["guild_name"]
                            guild.count_members = guild.count_members if data.get("count_members") is None else data[
                                "count_members"]
                            guild.guild_sets = guild.guild_sets if data.get("guild_sets") is None else data["guild_sets"]

                            guilds_list.append(guild)

                session.commit()

                return guilds_list[0] if is_dict else guilds_list

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

        return

    async def get_top_by_scores(self):
        with self.Session() as session:
            try:
                guilds = (select(Guilds)
                          .options(selectinload(Guilds.users))
                          .limit(20))

                res = session.scalars(guilds).all()
                if not res:
                    print("Can't get users in guild by scores")
                    return

                print(res)
                return res

            except:
                print("Something went wrong when get users top in guild by scores")
                print(traceback.format_exc())

        return

    ####################################   RELATIONSHIPS   ############################################


class RelationshipsDBase(DataBase):

    def __init__(self, echo_mode):
        super().__init__(echo_mode)
        self.guilds_db = GuildsDbase()
        self.users_db = UserDBase()

    async def add_relationship(self, data: Union[dict, list[dict]]) -> Any:
        """
        data = [{"users": list[ds_id],
                "guilds": list[guild_id}]]
        """

        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            try:
                for data in data:
                    received_users = await self.users_db.get_user_with_guilds(data["users"])
                    received_guilds = await self.guilds_db.get_guild_with_users(data["guilds"])

                    for user in received_users:
                        for guild in received_guilds:
                            if user not in guild.users:
                                guild.users.append(user)

                        print(user, guild)

                session.commit()

                return True

            except Exception:
                print(traceback.format_exc())
                return

    async def delete_relationship(self):
        pass

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

    data = {"ds_id": 785364734786,
            "username": "Nikita073_"}

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


async def test_get_top_by_scores(guilds_echo=False):
    db = GuildsDbase(guilds_echo)

    await db.get_top_by_scores()

    ####################################   RELATIONSHIPS TESTS   ############################################


async def test_add_relationship(rel_echo=False):
    db = RelationshipsDBase(rel_echo)

    users = [{"ds_id": 785364734786},
             {"ds_id": 674325879834}]

    guild = [{"guild_id": 785312593614209055}]

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

    # await test_get_top_by_scores(guilds_echo)

    ###################################################

    rel_echo = True

    # RELATIONSHIPS TESTS
    await test_add_relationship(rel_echo)


if __name__ == "__main__":
    echo = False
    engine = create_engine("sqlite:///DataBase.db", echo=echo)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.echo = True

    asyncio.run(main())
