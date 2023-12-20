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
        "ds_id": int}   (ds_id is unique identifier of Discord)

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """

        user_list = []
        is_dict = True if type(data) == dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            try:
                for data in data:
                    user = Users(username=data["username"], ds_id=data["ds_id"],
                                 scores=data["scores"] if data.get("scores") else 0,
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
        You can't get access to guilds with this function, please, use the
        get_user_with_guilds function

        If a dictionary was passed to the function, it will return a user object.
        If a list was passed, it will return a list of user objects.
        On error will return a None object.
        """

        is_dict = True if type(data) == dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:

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

        If a dictionary was passed to the function, it will return a user object with guilds.
        If a list was passed, it will return a list of user objects with guilds.
        On error will return a None object.
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
                                .options(selectinload(Users.guilds))
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
        Calls staticmethod get_user_static

        get_user_static:
            A static method that gets user from database
            Called from others async functions

            Accepts session and data.
            Data have to have at least one parameter: ds_id or username.

            Attention:
            Search by ds_id is the preferred authentication method.
            You can't get access to guilds with this function, please, use the
            get_user_with_guilds function

            If a dictionary was passed to the function, it will return a user object.
            If a list was passed, it will return a list of user objects.
            On error will return a None object.
        """

        with self.Session() as session:
            user = self.get_user_static(session, data)
            if user:
                print(user)

            return user

    async def get_user_with_guilds(self, data: Union[dict, list[dict]]) -> Union[Users, list[Users], None]:
        """
        Calls staticmethod get_user_static_with_guilds

        get_user_static_with_guilds:
            A static method that gets the user from the database with the guilds in which he belongs.
            Use selectinload parameter for query
            Called from others async functions

            Accepts session and data.
            Data have to have at least one parameter: ds_id or username.

            Attention:
            Search by ds_id is the preferred authentication method.

            If a dictionary was passed to the function, it will return a user object with guilds.
            If a list was passed, it will return a list of user objects with guilds.
            On error will return a None object.
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
        You can't change any relationships with this function, please, use RelationshipsDBase
        class to manage relationships

        Returns a User model object if the operation is successful,
        or None if there is an error
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
                            user.experience = user.experience if data.get("experience") is None else data[
                                "experience"]

                session.commit()

                print(users)
                return users

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

    async def get_top_users_by_scores(self) -> Union[list[Users], None]:
        """
        Gets the top users from database by scores from all guilds

        Returns a list of Users from scores top if the operation is
        successful, or None if error.
        """
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
                            select(Guilds)
                            .options(selectinload(Guilds.users))
                            .filter_by(guild_id=data["guild_id"]))

                        guild = session.scalars(guild).first()
                        if not guild:
                            print("Can't find guild by discord id in database")
                            return

                        guild_list.append(guild)

                    elif "guild_name" in data.keys():
                        guild = (
                            select(Guilds)
                            .options(selectinload(Guilds.users))
                            .filter_by(guild_name=data["guild_name"]))

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
                            guild.guild_name = guild.guild_name if data.get("guild_name") is None else data[
                                "guild_name"]
                            guild.count_members = guild.count_members if data.get("count_members") is None else \
                                data[
                                    "count_members"]
                            guild.guild_sets = guild.guild_sets if data.get("guild_sets") is None else data[
                                "guild_sets"]

                            guilds_list.append(guild)

                session.commit()

                return guilds_list[0] if is_dict else guilds_list

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

        return

    async def get_top_users_by_scores(self, guild_id: int):
        user_list = []
        with self.Session() as session:
            try:
                guilds = (select(Guilds)
                          .options(selectinload(Guilds.users))
                          .filter_by(guild_id=guild_id)
                          )

                res = session.scalars(guilds).first().users
                if not res:
                    print("Can't get users in guild by scores")
                    return

                for user in res:
                    if len(user_list) != 20:
                        user_data = {"username": user.username,
                                     "ds_id": user.ds_id,
                                     "scores": user.scores,
                                     "experience": user.experience}
                        user_list.append(user_data)
                    else:
                        break

                sorted_res = sorted(user_list, key=lambda x: x["scores"], reverse=True)

                print(sorted_res)
                return res

            except:
                print("Something went wrong when get users top in guild by scores")
                print(traceback.format_exc())

        return

    ####################################   RELATIONSHIPS   ############################################


class RelationshipsDBase(DataBase):

    def __init__(self, echo_mode):
        super().__init__(echo_mode)
        self.guilds_db = GuildsDbase(echo_mode)
        self.users_db = UserDBase(echo_mode)

    async def add_relationship(self, data: Union[dict, list[dict]]) -> Union[True, None]:
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
                    received_users = self.users_db.get_user_static_with_guilds(session, data["users"])
                    received_guilds = self.guilds_db.get_guild_static_with_users(session, data["guilds"])

                    for guild in received_guilds:
                        for user in received_users:
                            guild.users.append(user)

                    session.commit()

                return True

            except Exception:
                print("Something went wrong when add relationships between users and guilds")
                print(traceback.format_exc())

        return

    async def delete_relationship(self, data):
        # data = {"ds_id": int,
        #         "guild_id": int}
        with self.Session() as session:
            try:
                user = self.users_db.get_user_static_with_guilds(session, data["users"])
                guild = self.guilds_db.get_guild_static_with_users(session, data["guilds"])

                user.remove(guild)

                session.commit()

                return True

            except Exception:
                print("Something went wrong when delete relationships between users and guilds")
                print(traceback.format_exc())

        return
