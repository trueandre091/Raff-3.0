import ast
import asyncio
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
        guild_id: int = None,
        username: str = None,
        load: bool = True,
        load_guilds: bool = False,
        load_sem: bool = False,
    ):
        self._ds_id: int = ds_id
        self._username: str = username
        self.req_guild_id = guild_id
        self._db_user: Users | None = None

        self._guilds: list[Guild] = list()
        self._SEMs: list[SEM] = list()

        self.__created_at: datetime | None = None
        self.__updated_at: datetime | None = None

        self._load: bool = load
        self._load_sem: bool = load_sem
        self._load_guilds: bool = True if self._load_sem or self.req_guild_id or load_guilds else False

        self._conn: DBConnection = DBConnection()

        if self._load:
            self.add(self.req_guild_id, self._load_guilds, self._load_sem)

    def __del__(self):
        self.update()

    def __eq__(self, other) -> bool:
        return self.ds_id == other.ds_id

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
        return self._SEMs

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

    @property
    def db_user(self) -> Users | None:
        """DB Users model"""
        return self._db_user

    @db_user.setter
    def db_user(self, new_db_user: Users):
        self._db_user = new_db_user

    def add(self, guild_id: int | None, load_guilds: bool, load_sem: bool):
        with self._conn.Session() as session:
            try:
                user = Users(ds_id=self._ds_id, username=self._username)

                session.add(user)
                session.commit()

                self.db_user = user
                self._username = user.username
                self.__updated_at = user.updated_at
                self.__created_at = user.created_at

            except IntegrityError:
                session.rollback()
                user = self.load_info(load_guilds, load_sem)
                if user is not None:
                    logger.debug(f"User {self.ds_id} already in database")
                else:
                    logger.exception(
                        f"Something went wrong when get user {self.ds_id} for add function\n",
                        IntegrityError,
                    )

            except Exception as e:
                logger.exception(f"Something went wrong when adding user {self.ds_id}", e)

            if guild_id is not None:
                asyncio.get_event_loop().create_task(self.add_relationship(guild_id))

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
                        logger.error("User {self.ds_id} or sem not found")
                        return

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
                                        guild
                                    )
                                    guild_list.append(guild)
                                    SEMs_list.append(
                                        SEM(guild, sem.scores, sem.experience, sem.messages, sem)
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

                    if not user:
                        logger.error(f"User {self.ds_id} not found")
                        return

                    guild_list = []

                    for guild in user.guilds:
                        guild_list.append(
                            Guild(
                                guild.guild_id,
                                guild.guild_name,
                                guild.count_members,
                                guild.guild_sets,
                                guild
                            )
                        )

                    self._guilds = guild_list

                else:
                    query = select(Users).filter_by(ds_id=self._ds_id)
                    user = session.scalars(query).first()

                    if not user:
                        logger.error(f"User {self.ds_id} not found")
                        return

                self.db_user = user
                self._username = user.username
                self.__updated_at = user.updated_at
                self.__created_at = user.created_at

                return self

            except Exception as e:
                logger.exception("Error when get info about user", e)
                return None

    def update(self):
        if self._db_user is None:
            return

        with self._conn.Session() as session:
            user = select(Users).filter_by(ds_id=self.ds_id)
            user = session.scalars(user).first()

            if not user:
                logger.error(f"User {self.ds_id} not found")
                return

            guilds_list = []
            if len(self.guilds) > 0:
                for guild in self.guilds:
                    guild = select(Guilds).filter_by(guild_id=guild.guild_id)
                    guild = session.scalars(guild).first()

                    if not guild:
                        logger.error(f"Guild {guild.guild_id} not found")
                        return

                    guilds_list.append(guild)

            if len(self.SEMs) > 0:
                for sem in self.SEMs:
                    db_sem = select(Guild_User).where(Guild_User.ds_id == self.ds_id, Guild_User.guild_id == sem.guild.guild_id)
                    db_sem = session.scalars(db_sem).first()

                    db_sem.scores = sem.scores
                    db_sem.experience = sem.experience
                    db_sem.messages = sem.messages

                    if not db_sem:
                        logger.error(f"SEM for user {self.ds_id} not found")
                        return

            user.username = self.username
            user.guilds = guilds_list

            session.commit()

    async def add_relationship(self, guild_id: int):
        if guild_id in self._guilds:
            return

        with self._conn.Session() as session:
            try:
                query = select(Guilds).filter_by(guild_id=guild_id)
                guild = session.scalars(query).first()

                if not guild:
                    logger.error(f"Guild {guild_id=} not found")
                    return

            except Exception as e:
                logger.exception(f"Something went wrong when get guild {guild_id=}", e)
                return

        guild: Guild = Guild(guild_id, guild.guild_name, guild.count_members, guild.guild_sets, guild)
        self._guilds.append(guild)

        return guild


class Guild:
    def __init__(
        self,
        guild_id: int,
        guild_name: str = None,
        count_members: int = None,
        guild_sets: dict = None,
        db_guild: Guilds = None
    ):
        self._guild_id: int = guild_id
        self._guild_name: str | None = guild_name
        self._count_members: int | None = count_members
        self._guild_sets: dict | None = guild_sets
        self._db_guild: Guilds | None = db_guild

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
    def created_at(self) -> datetime:
        """Record creation time"""
        return self.__created_at

    @property
    def updated_at(self) -> datetime:
        """Record update time"""
        return self.__updated_at

    @property
    def db_guild(self) -> Guilds:
        """DB Guilds model"""
        return self._db_guild

    @db_guild.setter
    def db_guild(self, new_db_guild) -> Guilds:
        self._db_guild = new_db_guild


class SEM:
    def __init__(self, guild: Guild, scores: int = 0, experience: int = 0, messages: int = 0, db_sem: Guild_User = None):
        self._scores: int = scores
        self._experience: int = experience
        self._messages: int = messages
        self._guild: Guild = guild
        self._db_sem: Guild_User | None = db_sem

    # def __eq__(self, other):
    #     pass
    #
    # def __del__(self):
    #     pass

    @property
    def scores(self) -> int:
        """Amount of scores for THIS user on THIS Guild"""
        return self._scores

    @scores.setter
    def scores(self, new_scores: int):
        self._scores = new_scores

    @property
    def experience(self) -> int:
        """Amount of experience for THIS user on THIS Guild"""
        return self._experience

    @experience.setter
    def experience(self, new_experience: int):
        self._experience = new_experience

    @property
    def messages(self) -> int:
        """Amount of messages for THIS user on THIS Guild"""
        return self._messages

    @messages.setter
    def messages(self, new_messages: int):
        self._messages = new_messages

    @property
    def guild(self):
        """Guild for THIS SEM"""
        return self._guild

    @property
    def db_sem(self) -> Guild_User | None:
        """DB record about scores, exp and messages"""
        return self._db_sem

    @db_sem.setter
    def db_sem(self, new_db_sem: Guild_User):
        self._db_sem = new_db_sem
