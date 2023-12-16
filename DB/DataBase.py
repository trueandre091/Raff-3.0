"""Database Management"""

import asyncio
from typing import Union
import traceback

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload

from models import Users, Guilds, Base


class DataBase:
    """Class for creating connection to database and managing it"""

    def __init__(self, echo_mode: bool = False):
        try:
            self.echo = echo_mode
            self.engine = create_engine("sqlite:///DataBase.db", echo=self.echo)
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
        "disc_id": int}   (disc_id is unique identifier of Discord)

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
                    user = Users(username=data["username"], disc_id=data["disc_id"],
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
        Data have to have at least one parameter: disc_id or username.

        Attention:
        Search by disc_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        is_dict = True if type(data) == dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:
                if "disc_id" in data.keys():
                    user = (select(Users)
                            .filter_by(disc_id=data["disc_id"]))
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
        Data have to have at least one parameter: disc_id or username.

        Attention:
        Search by disc_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        is_dict = True if type(data) == dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:
                if "disc_id" in data.keys():
                    user = (select(Users)
                            .options(selectinload(Users.guilds))
                            .filter_by(disc_id=data["disc_id"]))
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
        Data have to have at least one parameter: disc_id or username.

        Attention:
        Search by disc_id is the preferred authentication method.

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
        Data have to have at least one parameter: disc_id or username.

        Attention:
        Search by disc_id is the preferred authentication method.

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
        Data have to have at least one parameter: disc_id or username

        Attention:
        Search by disc_id is the preferred authentication method.

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
                        if data["disc_id"] == user.disc_id:
                            user.username = user.username if not data.get("username") else data["username"]
                            user.scores = user.scores if not data.get("scores") else data["scores"]
                            user.experience = user.experience if not data.get("experience") else data["experience"]

                session.commit()

                print(users)
                return users

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

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
                if "guild_id" in data.keys():
                    guild = (select(Guilds).options(selectinload(Users.guilds)).filter_by(guild_id=data["guild_id"]))
                    guild = session.scalars(guild).first()
                    if not guild:
                        print("Can't find guild by discord id in database")
                        return

                    guild_list.append(guild)

                elif "guild_name" in data.keys():
                    guild = (
                        select(Guilds).options(selectinload(Users.guilds)).filter_by(guild_name=data["guild_name"]))
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
                            guild.guild_name = guild.guild_name if not data.get("guild_name") else data["guild_name"]
                            guild.count_members = guild.count_members if not data.get("count_members") else data[
                                "count_members"]
                            guild.guild_sets = guild.guild_sets if not data.get("guild_sets") else data["guild_sets"]

                            guilds_list.append(guild)

                session.commit()

                return guilds_list[0] if is_dict else guilds_list

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

        return

    ####################################   RELATIONSHIPS   ############################################


class RelationshipsDBase(DataBase):
    async def add_relationship(self):
        pass

    async def delete_relationship(self):
        pass

    ####################################   USERS TESTS   ############################################


async def test_add_user():
    db = UserDBase(True)

    data = {"username": "TopNik_",
            "disc_id": 785364734786,
            "scores": 20}

    await db.add_user(data)


async def test_add_some_users():
    db = UserDBase(echo_mode=True)

    data = [{"username": "Andre",
             "disc_id": 674325879834},
            {"username": "Minion",
             "disc_id": 977865342843}]

    await db.add_user(data)


async def test_get_user():
    db = UserDBase(echo_mode=True)

    data = {"disc_id": 785364734786}

    await db.get_user(data)


async def test_get_some_users():
    db = UserDBase(echo_mode=True)

    data = [{"disc_id": 674325879834},
            {"disc_id": 977865342843}]

    await db.get_user(data)


async def test_get_user_with_guilds():
    db = UserDBase(echo_mode=True)

    data = {"disc_id": 785364734786}

    res = await db.get_user_with_guilds(data)

    print(res.guilds)


async def test_get_some_users_with_guilds():
    db = UserDBase(echo_mode=True)

    data = [{"disc_id": 674325879834},
            {"disc_id": 977865342843}]

    res = await db.get_user_with_guilds(data)

    for user in res:
        print(user.guilds)


async def test_update_user():
    db = UserDBase(True)

    data = {"disc_id": 785364734786,
            "username": "Nikita073_"}

    await db.update_user(data)


async def test_update_some_users():
    db = UserDBase(True)

    data = [{"disc_id": 674325879834,
             "username": "андре",
             "scores": 10_000},
            {"disc_id": 977865342843,
             "experience": 1_000}]

    await db.update_user(data)

    ####################################   GUILDS TESTS   ############################################


async def test_add_guild():
    db = GuildsDbase(echo_mode=True)

    data = {"guild_id": 785312593614209055,
            "guild_name": "Homey Temple"}

    await db.add_guild(data)


async def test_add_some_guilds():
    db = GuildsDbase(True)

    data = [{"guild_id": 710525764470308975,
             "guild_name": "NetherWorld"}]

    await db.add_guild(data)

    ####################################   DATABASE TESTS   ############################################


async def main():
    # USERS TESTS
    await test_add_user()
    await test_add_some_users()

    # await test_get_user()
    # await test_get_some_users()

    # await test_get_user_with_guilds()
    # await test_get_some_users_with_guilds()

    # await test_update_user()
    # await test_update_some_users()

    ###################################################

    # GUILDS TESTS
    # await test_add_guild()
    # await test_add_some_guilds()


if __name__ == "__main__":
    echo = False
    engine = create_engine("sqlite:///DataBase.db", echo=echo)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.echo = True

    asyncio.run(main())
