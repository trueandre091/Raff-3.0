"""Database Management"""
from loguru import logger

from typing import Union, Sequence, Optional

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.exc import IntegrityError


from DB.models import Users, Guilds
from DB.JSONEnc import JsonEncoder


class DataBase:
    """Class for creating connection to database and managing it"""

    def __init__(self, echo_mode: bool = False):
        try:
            self.echo = echo_mode

            # FOR MAIN APP
            # self.engine = create_engine("sqlite:///DB/DataBase.db", echo=self.echo)

            # FOP TESTS
            self.engine = create_engine("sqlite:///DataBase.db", echo=self.echo)

            # FOR UTILS
            # self.engine = create_engine("sqlite:///../DB/DataBase.db", echo=self.echo)

            self.Session = sessionmaker(self.engine)
            logger.debug("Engine was successfully created")
        except Exception as e:
            logger.exception("Error creating engine or session", e)
            return

    ####################################   USERS   ############################################


class UserDBase(DataBase):
    """
    Class for managing with Users data

    You can choose echo mode by passing the echo_mode parameter
    """

    async def add_user(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[Users, list[Users], None]:
        """
        Adds a user to the database

        Accepts a dictionary or a list of dictionaries like:
        {"username": str,   required parameter  (user discord username)
        "ds_id": int,       required parameter  (ds_id is unique identifier of Discord)
        "scores": int,                          (user scores)
        "experience": int}                      (user experience)

        Returns a User model object if the operation is successful,
        or nothing if there is an error
        """
        if not data:
            data = kwargs

        user_list = []
        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            for data in data:
                try:
                    user = Users(
                        username=data["username"],
                        ds_id=data["ds_id"],
                        scores=data["scores"] if data.get("scores") else 0,
                        experience=data["experience"] if data.get("experience") else 0,
                        messages=data["messages"] if data.get("messages") else 0,
                    )

                    session.add(user)
                    session.commit()

                    user_list.append(user)
                    logger.debug(user)

                except IntegrityError:
                    session.rollback()
                    user = await self.get_user(data)
                    if user:
                        logger.debug(f"{user} already in database")
                        user_list.append(user)
                    else:
                        logger.exception(
                            "Something went wrong when get user for add function\n",
                            IntegrityError,
                        )

                        return

                except Exception as e:
                    logger.exception("Something went wrong when adding user", e)
                    return

        if len(user_list) != 0:
            return user_list[0] if is_dict else user_list

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

        is_dict = True if type(data) is dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:
                if "ds_id" in data.keys():
                    user = select(Users).filter_by(ds_id=data["ds_id"])
                    user = session.scalars(user).first()
                    if not user:
                        logger.error("Can't find user by discord id in database")
                        return

                    user_list.append(user)

                elif "username" in data.keys():
                    user = select(Users).filter_by(username=data["username"])
                    user = session.scalars(user).first()
                    if not user:
                        logger.error("Can't find user by username in database")
                        return

                    user_list.append(user)

                return user_list[0] if is_dict else user_list

        except Exception as e:
            logger.exception("Something went wrong when get user with guilds", e)

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

        is_dict = True if type(data) is dict else False
        user_list = []

        if is_dict:
            data = [data]

        try:
            for data in data:
                if type(data) is list:
                    for ds_id in data:
                        user = (
                            select(Users).options(selectinload(Users.guilds)).filter_by(ds_id=ds_id)
                        )

                        user = session.scalars(user).first()
                        if not user:
                            logger.error(
                                "Something went wrong when get user with guilds for relationship"
                            )
                            return

                        user_list.append(user)

                else:
                    if "ds_id" in data.keys():
                        user = (
                            select(Users)
                            .options(selectinload(Users.guilds))
                            .filter_by(ds_id=data["ds_id"])
                        )
                        user = session.scalars(user).first()
                        if not user:
                            logger.error("Can't find user by discord id in database")
                            return

                        user_list.append(user)

                    elif "username" in data.keys():
                        user = (
                            select(Users)
                            .options(selectinload(Users.guilds))
                            .filter_by(username=data["username"])
                        )
                        user = session.scalars(user).first()
                        if not user:
                            logger.error("Can't find user by username in database")
                            return

                        user_list.append(user)

            return user_list[0] if is_dict else user_list

        except Exception as e:
            logger.exception("Something went wrong when get user with guilds", e)

        return

    async def get_user(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[Users, list[Users], None]:
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

        if data is None:
            data = kwargs

        with self.Session() as session:
            user = self.get_user_static(session, data)
            if user:
                logger.debug(user)

            return user

    async def get_user_with_guilds(
        self, data: Union[dict, list[dict]] = None, **kwargs
    ) -> Union[Users, list[Users], None]:
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

        if data is None:
            data = kwargs

        with self.Session() as session:
            user = self.get_user_static_with_guilds(session, data)
            if user:
                logger.debug(user)

            return user

    async def get_all_users(self) -> Optional[list[Users]]:
        """
        Gets all users from database
        """
        with self.Session() as session:
            try:
                users = session.scalars(select(Users)).all()
                if not users:
                    logger.error("Can't find users in database")
                    return

                return users

            except Exception as e:
                logger.exception("Something went wrong when get all users", e)

    async def get_all_users_with_guilds(self) -> Optional[list[Users]]:
        """
        Gets all users with guilds from database
        """
        with self.Session() as session:
            try:
                query = select(Users).options(selectinload(Users.guilds))
                users = session.scalars(query).all()
                if not users:
                    logger.error("Can't find all users with guilds in database")
                    return

                return users

            except Exception as e:
                logger.exception("Something went wrong when get all users with guilds", e)

    async def update_user(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[Users, list[Users], None]:
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

        if data is None:
            data = kwargs

        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            users = self.get_user_static(session, data)
            try:
                for data in data:
                    for user in users:
                        if data["ds_id"] == user.ds_id:
                            user.username = (
                                user.username if data.get("username") is None else data["username"]
                            )
                            user.scores = (
                                user.scores if data.get("scores") is None else data["scores"]
                            )
                            user.experience = (
                                user.experience
                                if data.get("experience") is None
                                else data["experience"]
                            )
                            user.messages = (
                                user.messages if data.get("messages") is None else data["messages"]
                            )

                session.commit()

                logger.debug(users)
                return users

            except Exception as e:
                logger.exception("Something went wrong when update user", e)

    async def get_top_users_by_scores(self) -> Union[Sequence[Users], None]:
        """
        Gets the top users from database by scores from all guilds

        Returns a list of Users from scores top if the operation is
        successful, or None if error.
        """
        with self.Session() as session:
            try:
                users = select(Users).order_by(Users.scores.desc()).limit(20)
                res = session.scalars(users).all()
                if not res:
                    logger.error("Can't get top users by scores")
                    return

                return res

            except Exception as e:
                logger.error("Something went wrong when get top for users by scores\n", e)

        return

    async def get_top_users_by_messages(self) -> Union[Sequence[Users], None]:
        """
        Gets the top users from database by count of messages from all guilds

        Returns a list of Users from scores top if the operation is successful,
        or None if error.
        """
        with self.Session() as session:
            try:
                users = select(Users).order_by(Users.messages.desc()).limit(20)
                res = session.scalars(users).all()
                if not res:
                    logger.error("Can't get top users by messages")
                    return

                return res

            except Exception as e:
                logger.error("Something went wrong when get top for users by scores\n", e)

        return


####################################   GUILDS   ############################################


class GuildsDBase(DataBase):
    """
    Class for managing with Guilds data

    You can choose echo mode by passing the echo_mode parameter
    """

    async def add_guild(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[Guilds, list[Guilds], None]:
        """
        Adds a guild to the database

        Accepts a dictionary or a list of dictionaries like:

        {"guild_id": int,     required parameter  (name of the guild)
        "guild_name": str,    required parameter  (ds_id is unique identifier of Discord)
        "count_members": int,                     (count of users (members) on this guild)
        "guild_sets": str}                        (a string with a json string inside, contains server parameters)

        Returns a Guild model object if the operation is successful,
        or nothing if there is an error
        """

        if data is None:
            data = kwargs

        guilds_list = []
        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            for data in data:
                try:
                    guild = Guilds(
                        guild_id=data["guild_id"],
                        guild_name=data["guild_name"],
                        count_members=0
                        if data.get("count_members") is None
                        else data["count_members"],
                    )

                    session.add(guild)
                    session.commit()

                    guilds_list.append(guild)
                    logger.debug(guild)

                except IntegrityError:
                    session.rollback()
                    guild = await self.get_guild(data)
                    if guild:
                        logger.debug(f"{guild} already in database")
                        guilds_list.append(guild)
                    else:
                        logger.error(
                            "Something went wrong when get guild fo add function\n",
                            IntegrityError,
                        )

                        return

                except Exception as e:
                    logger.error("Something went wrong then adding guild\n", e)

        if len(guilds_list) != 0:
            return guilds_list[0] if is_dict else guilds_list

    @staticmethod
    def get_guild_static(session, data):
        """
        A static method that gets guild from database
        Called from others async functions

        Accepts session and data.
        Data have to have at least one parameter: guild_id or guild_name.

        Attention:
        Search by guild_id is the preferred authentication method.
        You can't get access to users with this function, please, use the
        get_guild_with_users function

        If a dictionary was passed to the function, it will return a guild object.
        If a list was passed, it will return a list of guilds objects.
        On error will return a None object.
        """
        guild_list = []
        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        try:
            for data in data:
                if "guild_id" in data.keys():
                    guild = select(Guilds).filter_by(guild_id=data["guild_id"])

                    guild = session.scalars(guild).first()
                    if not guild:
                        logger.error("Can't find guild by discord id in database")
                        return

                    guild_list.append(guild)

                elif "guild_name" in data.keys():
                    guild = select(Guilds).filter_by(guild_name=data["guild_name"])
                    guild = session.scalars(guild).first()
                    if not guild:
                        logger.error("Can't find guild by guild name in database")
                        return

                    guild_list.append(guild)

            return guild_list[0] if is_dict else guild_list

        except Exception as e:
            logger.exception("Something went wrong when get guild\n", e)

        return

    @staticmethod
    def get_guild_static_with_users(session, data):
        """
        A static method that gets the guild from the database along with the users that are on this guild.
        Use selectinload parameter for query
        Called from others async functions

        Accepts session and data.
        Data have to have at least one parameter: guild_id or guild_name.

        Attention:
        Search by guild_id is the preferred authentication method.

        If a dictionary was passed to the function, it will return a guild object with users.
        If a list was passed, it will return a list of guilds objects with users.
        On error will return a None object.
        """
        guild_list = []
        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        try:
            for data in data:
                if type(data) is list:
                    for guild_id in data:
                        guild = (
                            select(Guilds)
                            .options(selectinload(Guilds.users))
                            .filter_by(guild_id=guild_id)
                        )

                        guild = session.scalars(guild).first()
                        if not guild:
                            logger.error("Something went wrong when get guild for relationship")
                            return

                        guild_list.append(guild)

                else:
                    if "guild_id" in data.keys():
                        guild = (
                            select(Guilds)
                            .options(selectinload(Guilds.users))
                            .filter_by(guild_id=data["guild_id"])
                        )

                        guild = session.scalars(guild).first()
                        if not guild:
                            logger.error("Can't find guild with users by discord id in database")
                            return

                        guild_list.append(guild)

                    elif "guild_name" in data.keys():
                        guild = (
                            select(Guilds)
                            .options(selectinload(Guilds.users))
                            .filter_by(guild_name=data["guild_name"])
                        )

                        guild = session.scalars(guild).first()
                        if not guild:
                            logger.error("Can't find guild with users by guild name in database")
                            return

                        guild_list.append(guild)

            return guild_list[0] if is_dict else guild_list

        except Exception as e:
            logger.error("Something went wrong when get guild\n", e)

        return

    async def get_guild(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[Guilds, list[Guilds], None]:
        """
        Calls staticmethod get_guild_static

        get_guild_static:
            A static method that gets guild from database
            Called from others async functions

            Accepts session and data.
            Data have to have at least one parameter: guild_id or guild_name.

            Attention:
            Search by guild_id is the preferred authentication method.
            You can't get access to users with this function, please, use the
            get_guild_with_users function

            If a dictionary was passed to the function, it will return a guild object.
            If a list was passed, it will return a list of guilds objects.
            On error will return a None object.
        """

        if data is None:
            data = kwargs

        with self.Session() as session:
            guild = self.get_guild_static(session, data)
            if guild:
                logger.debug(guild)

            return guild

    async def get_guild_with_users(
        self, data: Union[dict, list[dict]] = None, **kwargs
    ) -> Union[Guilds, list[Guilds], None]:
        """
        Calls staticmethod get_guild_static_with_users

        get_guild_static_with_users:
            A static method that gets the guild from the database along with the users that are on this guild.
            Use selectinload parameter for query
            Called from others async functions

            Accepts session and data.
            Data have to have at least one parameter: guild_id or guild_name.

            Attention:
            Search by guild_id is the preferred authentication method.

            If a dictionary was passed to the function, it will return a guild object with users.
            If a list was passed, it will return a list of guilds objects with users.
            On error will return a None object.
        """

        if data is None:
            data = kwargs

        with self.Session() as session:
            guild = self.get_guild_static_with_users(session, data)
            if guild:
                logger.debug(guild)

            return guild

    async def get_all_guilds(self) -> Optional[list[Guilds]]:
        """
        Gets all guilds from database
        """
        with self.Session() as session:
            try:
                guilds = session.scalars(select(Guilds)).all()
                if not guilds:
                    logger.error("Can't find all guilds in database")
                    return

                return guilds

            except Exception as e:
                logger.error("Something went wrong when get all guilds\n", e)

    async def get_all_guilds_with_users(self) -> Optional[list[Guilds]]:
        """
        Gets all guilds from database with users
        """
        with self.Session() as session:
            try:
                query = select(Guilds).options(selectinload(Guilds.users))
                guilds = session.scalars(query).all()
                if not guilds:
                    logger.error("Can't find all guilds with users in database")
                    return

                return guilds

            except Exception as e:
                logger.error("Something went wrong when get all guilds with users\n", e)

    async def update_guild(
        self, data: Union[dict, list[dict]] = None, **kwargs
    ) -> Union[Guilds, list[Guilds], None]:
        """
        Updates guild from database. Use get_guild_static for getting user.

        Accepts data.
        Data have to have at least one parameter: guild_id or guild_name

        Attention:
        Search by guild_id is the preferred authentication method.
        You can't change any relationships with this function, please, use RelationshipsDBase
        class to manage relationships

        Returns a guild model object if the operation is successful,
        or None if there is an error
        """

        if data is None:
            data = kwargs

        guilds_list = []
        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            guilds = self.get_guild_static(session, data)
            try:
                for data in data:
                    for guild in guilds:
                        if data["guild_id"] == guild.guild_id:
                            if isinstance(data.get("guild_sets", None), dict):
                                enc = JsonEncoder()
                                data["guild_sets"] = enc.code_to_json(data["guild_sets"])

                            guild.guild_name = (
                                guild.guild_name
                                if data.get("guild_name") is None
                                else data["guild_name"]
                            )
                            guild.count_members = (
                                guild.count_members
                                if data.get("count_members") is None
                                else data["count_members"]
                            )
                            guild.guild_sets = (
                                guild.guild_sets
                                if data.get("guild_sets") is None
                                else data["guild_sets"]
                            )

                            guilds_list.append(guild)

                session.commit()

                return guilds_list[0] if is_dict else guilds_list

            except Exception as e:
                logger.error("Something went wrong when update guild\n", e)

        return

    async def get_top_users_by_scores(self, guild_id: int):
        """
        Gets the top users from database by scores from this guild

        Receives guild_id for getting guild

        Returns a list of Users from scores top if the operation is
        successful, or None if error.
        """
        user_list = []
        with self.Session() as session:
            try:
                guilds = (
                    select(Guilds).options(selectinload(Guilds.users)).filter_by(guild_id=guild_id)
                )

                res = session.scalars(guilds).first()
                if not res:
                    logger.error("Can't get users in guild by scores")
                    return

                res = res.users

                for user in res:
                    user_list.append(user)

                sorted_res = sorted(user_list, key=lambda x: x.scores, reverse=True)
                sorted_res = sorted_res[:20]

                logger.debug(sorted_res)
                return sorted_res

            except Exception as e:
                logger.error("Something went wrong when get users top in guild by scores\n", e)

        return

    async def get_top_users_by_messages(self, guild_id: int):
        """
        Gets the top users from database by count of messages from this guild

        Receives guild_id for getting guild

        Returns a list of Users from count of messages top if the operation is
        successful, or None if error.
        """
        user_list = []
        with self.Session() as session:
            try:
                guilds = (
                    select(Guilds).options(selectinload(Guilds.users)).filter_by(guild_id=guild_id)
                )

                res = session.scalars(guilds).first()
                if not res:
                    logger.error("Can't get users in guild by count of messages")
                    return

                res = res.users

                for user in res:
                    user_list.append(user)

                sorted_res = sorted(user_list, key=lambda x: x.messages, reverse=True)
                sorted_res = sorted_res[:20]

                logger.debug(sorted_res)
                return sorted_res

            except Exception as e:
                logger.error(
                    "Something went wrong when get users top in guild by count of messages\n",
                    e,
                )

        return

    ####################################   RELATIONSHIPS   ############################################


class RelationshipsDBase(DataBase):
    """
    Class for managing with relationships

    This class inherits from UserDBase and GuildDBase classes and use their methods

    You can choose echo mode by passing the echo_mode parameter
    """

    def __init__(self, echo_mode: bool = False):
        super().__init__(echo_mode)
        self.guilds_db = GuildsDBase(echo_mode)
        self.users_db = UserDBase(echo_mode)

    async def add_relationship(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[True, None]:
        """
        Adds a relationship between the user and the guild

        Gets a complex data structure:

        data = [{"users": list[{ds_id: int}],
                "guilds": list[{guild_id: int}]}
                ]

        Returns True if operation was successful and None if there was an error
        """

        if data is None:
            data = kwargs

        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            try:
                for data in data:
                    received_users = self.users_db.get_user_static_with_guilds(
                        session, data["users"]
                    )
                    received_guilds = self.guilds_db.get_guild_static_with_users(
                        session, data["guilds"]
                    )

                    if type(received_users) is not list:
                        received_users = [received_users]
                    if type(received_guilds) is not list:
                        received_guilds = [received_guilds]

                    for guild in received_guilds:
                        for user in received_users:
                            guild.users.append(user)
                            logger.debug(str(guild) + " " + str(user))

                    session.commit()

                return True

            except Exception as e:
                logger.error(
                    "Something went wrong when add relationships between users and guilds\n",
                    e,
                )

        return

    async def delete_relationship(self, data: Union[dict, list[dict]] = None, **kwargs) -> Union[True, None]:
        """
        Deletes a relationship between the user and the guild

        Gets a complex data structure:

        data = [{"users": list[{ds_id: int}],
                "guilds": list[{guild_id: int}]}
                ]

        Returns True if operation was successful and None if there was an error
        """

        if data is None:
            data = kwargs

        is_dict = True if type(data) is dict else False

        if is_dict:
            data = [data]

        with self.Session() as session:
            try:
                for data in data:
                    received_users = self.users_db.get_user_static_with_guilds(
                        session, data["users"]
                    )
                    received_guilds = self.guilds_db.get_guild_static_with_users(
                        session, data["guilds"]
                    )

                    for guild in received_guilds:
                        for user in received_users:
                            if user in guild.users:
                                guild.users.remove(user)
                                logger.debug(str(guild) + " " + str(user))

                    session.commit()

                return True

            except Exception as e:
                logger.error(
                    "Something went wrong when delete relationships between users and guilds\n",
                    e,
                )

        return