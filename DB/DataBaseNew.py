import ast
import asyncio
from asgiref.sync import async_to_sync
from loguru import logger

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload, joinedload, join, contains_eager
from sqlalchemy.exc import IntegrityError

from DB.models import Users, Guilds, Guild_User

from datetime import datetime


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class DBConnection:
    """Class for creating connection to database"""

    def __init__(self, echo_mode=False):
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
            logger.exception("Error creating Engine or Session", e)
            return


class User:
    def __init__(
        self,
        ds_id: int,
        username: str = None,
        load: bool = True,
        load_guilds: bool = False,
        load_sem: bool = False,
    ):
        self._ds_id: int = ds_id
        self._username: str | None = username

        self._guilds: list[Guild] = list()
        self._SEMs: list[SEM] = list()

        self.__created_at: datetime | None = None
        self.__updated_at: datetime | None = None

        self._load: bool = load
        self._load_sem: bool = load_sem
        self._load_guilds: bool = True if self._load_sem or load_guilds else False

        self._conn: DBConnection = DBConnection()

        if self._load:
            self.load_info(self._load_guilds, self._load_sem)

    @property
    def ds_id(self) -> int | None:
        """User Discord id"""
        return self._ds_id

    @ds_id.setter
    def ds_id(self, new_ds_id: int):
        self._ds_id = new_ds_id

    @property
    def username(self) -> str | None:
        """User Discord username"""
        return self._username

    @username.setter
    def username(self, new_username: str):
        self._username = new_username

    @property
    def guilds(self):
        return self._guilds

    @guilds.setter
    def guilds(self, new_guilds):
        self._guilds = new_guilds

    @property
    def SEMs(self):
        return self.SEMs

    @SEMs.setter
    def SEMs(self, new_SEMs):
        self._SEMs = new_SEMs

    @property
    def created_at(self) -> datetime:
        """User record creation time"""
        return self.__created_at

    @property
    def updated_at(self) -> datetime:
        """User record update time"""
        return self.__updated_at

    def load_info(self, load_guilds: bool = False, load_sem: bool = False):
        with self._conn.Session() as session:
            try:
                if load_sem:
                    query = (
                        select(Users)
                        .options(selectinload(Users.guilds))
                        .filter_by(ds_id=self._ds_id)
                    )

                    query_scm = select(Guild_User).filter_by(ds_id=self._ds_id)

                    sem_res = session.scalars(query_scm).all()
                    user = session.scalars(query).first()

                    if not user or not sem_res:
                        raise "User or sem not found"

                    guild_list = []
                    SEMs_list = []

                    if user.guilds is not None:
                        for guild in user.guilds:
                            for sem in sem_res:
                                if guild.guild_id == sem.guild_id:
                                    guild = Guild(
                                        guild.guild_id,
                                        guild.guild_name,
                                        guild.count_members,
                                        guild.guild_sets,
                                    )
                                    guild_list.append(guild)
                                    SEMs_list.append(
                                        SEM(sem.scores, sem.experience, sem.messages, guild)
                                    )

                    self._guilds = guild_list
                    self.SEMs = SEMs_list

                elif load_guilds:
                    query = (
                        select(Users)
                        .options(selectinload(Users.guilds))
                        .filter_by(ds_id=self._ds_id)
                    )

                    user = session.scalars(query).first()

                    guild_list = []

                    for guild in user.guilds:
                        guild_list.append(
                            Guild(
                                guild.guild_id,
                                guild.guild_name,
                                guild.count_members,
                                guild.guild_sets,
                            )
                        )

                    self._guilds = guild_list

                else:
                    query = select(Users).filter_by(ds_id=self._ds_id)
                    user = session.scalars(query).first()

                self._username = user.username
                self.__updated_at = user.updated_at
                self.__created_at = user.created_at

            except Exception as e:
                logger.exception("Error when get info about user", e)


class Guild:
    def __init__(
        self,
        guild_id: int,
        guild_name: str = None,
        count_members: int = None,
        guild_sets: dict = None,
    ):
        self._guild_id: int = guild_id
        self._guild_name: str | None = guild_name
        self._count_members: int | None = count_members
        self._guild_sets: dict | None = guild_sets

        self._users: list[User] | None = None

        self.__created_at: datetime | None = None
        self.__updated_at: datetime | None = None

    @property
    def guild_id(self) -> int:
        """Guild Discord id"""
        return self._guild_id

    @guild_id.setter
    def guild_id(self, new_guild_id: int):
        self._guild_id = new_guild_id

    @property
    def guild_name(self) -> str | None:
        """Guild Discord name"""
        return self._guild_name

    @guild_name.setter
    def guild_name(self, new_guild_name: str):
        self._guild_name = new_guild_name

    @property
    def count_members(self):
        """Number of Guild members"""
        return self._count_members

    @count_members.setter
    def count_members(self, new_count_members: int):
        self._count_members = new_count_members

    @property
    def guild_sets(self):
        """Settings of Guild"""
        return self._guild_sets

    @guild_sets.setter
    def guild_sets(self, new_guild_sets: dict):
        self._guild_sets = new_guild_sets

    @property
    def created_at(self):
        return self.__created_at

    @property
    def updated_at(self):
        return self.__updated_at


class SEM:
    def __init__(self, scores: int, experience: int, messages: int, guild: Guild):
        self._scores: int = scores
        self._experience: int = experience
        self._messages: int = messages
        self._guild: Guild = guild

    @property
    def scores(self) -> int:
        """User scores"""
        return self._scores

    @scores.setter
    def scores(self, new_scores: int):
        self._scores = new_scores

    @property
    def experience(self) -> int:
        """User experience"""
        return self._experience

    @experience.setter
    def experience(self, new_experience: int):
        self._experience = new_experience

    @property
    def messages(self) -> int:
        """User messages"""
        return self._messages

    @messages.setter
    def messages(self, new_messages: int):
        self._messages = new_messages
