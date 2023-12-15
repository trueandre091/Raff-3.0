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

    def __init__(self, echo: bool = False):
        try:
            self.echo = echo
            self.engine = create_engine("sqlite:///DataBase.db", echo=self.echo)
            self.Session = sessionmaker(self.engine)
        except:
            raise "Error creating an engine or connecting to database"

    ####################################   USERS   ############################################


class UserDBase(DataBase):
    async def add_user(self, data: dict) -> Union[Users, None]:
        """
        Adds a user to the database

        Accepts a dictionary like:
        {"username": str,
        "disc_id": int}   (disc_id is unique identifier of Discord)

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """
        with self.Session() as session:
            try:
                user = Users(username=data["username"], disc_id=data["disc_id"])
                print(user)

                session.add(user)
                session.commit()

                return user
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

        try:
            if "disc_id" in data.keys():
                user = (select(Users)
                        .filter_by(disc_id=data["disc_id"]))
                user = session.scalars(user).first()
                if not user:
                    print("Can't find user by discord id in database")
                    return

                return user

            elif "username" in data.keys():
                user = (select(Users)
                        .filter_by(username=data["username"]))
                user = session.scalars(user).first()
                if not user:
                    print("Can't find user by username in database")
                    return

                return user

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

        try:
            if "disc_id" in data.keys():
                user = (select(Users)
                        .options(selectinload(Users.guilds_in_user))
                        .filter_by(disc_id=data["disc_id"]))
                user = session.scalars(user).first()
                if not user:
                    print("Can't find user by discord id in database")
                    return

                return user

            elif "username" in data.keys():
                user = (select(Users)
                        .options(selectinload(Users.guilds_in_user))
                        .filter_by(username=data["username"]))
                user = session.scalars(user).first()
                if not user:
                    print("Can't find user by username in database")
                    return

                return user

        except Exception:
            print("Something went wrong when get user")
            print(traceback.format_exc())

        return

    async def get_user(self, data: dict) -> Union[Users, None]:
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

    async def get_user_with_guilds(self, data) -> Union[Users, None]:
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

    async def update_user(self, data: dict) -> Union[Users, None]:
        """
        Updates user from database. Use get_user_static for getting user.

        Accepts data.
        Data have to have at least one parameter: disc_id or username

        Attention:
        Search by disc_id is the preferred authentication method.

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """
        with self.Session() as session:
            user = self.get_user_static(session, data)
            if user:
                try:
                    user.username = lambda _: user.username if not data.get("username") else data["username"]
                    user.scores = lambda _: user.username if not data.get("scores") else data["scores"]
                    user.experience = lambda _: user.username if not data.get("experience") else data["experience"]

                    session.commit()

                    print(user)
                    return user

                except Exception:
                    print("Something went wrong when update user")
                    print(traceback.format_exc())

            else:
                return user

    ####################################   GUILDS   ############################################


class GuildsDbase(DataBase):
    async def add_guild(self, data: dict) -> Union[Guilds, None]:
        with self.Session() as session:
            try:
                guild = Guilds(guild_id=data["guild_id"],
                               guild_name=data["guild_name"],
                               count_members=(data["count_members"] if data.get("count_members") else 0))

                session.add(guild)
                session.commit()

                return guild

            except Exception:
                print("Something went wrong then adding guild")
                print(traceback.format_exc())

        return

    @staticmethod
    def get_guild_static(session, data):
        try:
            if "guild_id" in data.keys():
                guild = select(Guilds).filter_by(guild_id=data["guild_id"])
                guild = session.scalars(guild).first()
                if not guild:
                    print("Can't find guild by discord id in database")
                    return

                return guild

            elif "guild_name" in data.keys():
                guild = select(Guilds).filter_by(guild_name=data["guild_name"])
                guild = session.scalars(guild).first()
                if not guild:
                    print("Can't find guild by guild name in database")
                    return

                return guild

        except Exception:
            print("Something went wrong when get guild")
            print(traceback.format_exc())

        return

    async def get_guild(self, data: dict) -> Union[Guilds, None]:
        with self.Session() as session:
            return self.get_guild_static(session, data)

    async def update_guild(self, data: dict) -> Union[Guilds, None]:
        with self.Session() as session:
            try:
                guild = self.get_guild_static(session, data)

                guild.guild_name = lambda _: guild.guild_name if not data.get("guild_name") else data["guild_name"]
                guild.count_members = lambda _: guild.count_members if not data.get("count_members") else data[
                    "count_members"]
                guild.guild_sets = lambda _: guild.guild_sets if not data.get("guild_sets") else data["guild_sets"]

                session.commit()

                return guild

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
    db = UserDBase(echo=True)

    data = {"username": "TopNik_",
            "disc_id": 785364734786}

    await db.add_user(data)

    # if res:
    #     print("Successfully added new user")
    # else:
    #     print("Error when printing res or res is None", res)


async def test_add_some_users():
    pass


async def test_get_user():
    db = UserDBase(echo=True)

    data = {"disc_id": 785364734786}

    await db.get_user(data)


async def test_get_some_users():
    pass


async def test_get_user_with_guilds():
    db = UserDBase(echo=True)

    data = {"disc_id": 785364734786}

    res = await db.get_user_with_guilds(data)

    print(res.guilds_in_user)


async def test_get_some_users_with_guilds():
    pass


async def test_update_user():
    pass


async def test_update_some_users():
    pass

    ####################################   GUILDS TESTS   ############################################


async def test_add_guild():
    db = GuildsDbase(echo=True)

    data = {"guild_id": 874365893234,
            "guild_name": "Homey Temple"}

    await db.add_guild(data)


async def main():
    # USERS TESTS
    await test_add_user()
    # await test_add_some_users()

    await test_get_user()
    # await test_get_some_users()

    await test_get_user_with_guilds()
    # await test_get_some_users_with_guilds()

    # await test_update_user()
    # await test_update_some_users()

    ###################################################

    # GUILDS TESTS
    # await test_add_guild()


if __name__ == "__main__":
    echo = False
    engine = create_engine("sqlite:///DataBase.db", echo=echo)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    engine.echo = True

    asyncio.run(main())
