from loguru import logger

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload, joinedload, join, contains_eager
from sqlalchemy.exc import IntegrityError

from DB.models import Users, Guilds, Guild_User

from datetime import datetime
from DB.JSONEnc import JsonEncoder


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
        load_guilds: bool = False,
        load_sem: bool = False,
        db_user: Users = None,
    ):
        self._ds_id: int = ds_id
        self._username: str = username
        self.guild_id = guild_id
        self._db_user: Users | None = db_user

        self._guilds: list[Guild] = list()
        self._SEMs: list[SEM] = list()

        self.__created_at: datetime | None = None
        self.__updated_at: datetime | None = None

        self._load_sem: bool = load_sem
        self._load_guilds: bool = True if self._load_sem or self.guild_id or load_guilds else False

        self._conn: DBConnection = DBConnection()

        self.add(self.guild_id, self._load_guilds, self._load_sem)

    def __del__(self):
        self.update()

    def __eq__(self, other) -> bool:
        return self.ds_id == other.ds_id

    def __repr__(self):
        return f"<User {self.username}, {self.ds_id}>"

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
                user = Users(ds_id=self.ds_id, username=self.username)

                session.add(user)
                session.commit()

                self.db_user = user
                self._username = user.username
                self.__updated_at = user.updated_at
                self.__created_at = user.created_at

            except IntegrityError:
                session.rollback()
                user = self.load(load_guilds, load_sem)
                if user is not None:
                    logger.debug(f"User {self} already in database")
                else:
                    logger.exception(
                        f"Something went wrong when get user {self} for add function\n",
                        IntegrityError,
                    )

            except Exception as e:
                logger.exception(f"Something went wrong when adding user {self}", e)

            if guild_id is not None:
                self.add_relationship(guild_id)

    def load(self, load_guilds: bool = False, load_sem: bool = False):
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

                    if not user or sem_res is None:
                        logger.error(f"User {self} or sem not found")
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
                                        guild,
                                    )
                                    guild_list.append(guild)
                                    SEMs_list.append(
                                        SEM(
                                            guild=guild,
                                            scores=sem.scores,
                                            experience=sem.experience,
                                            messages=sem.messages,
                                            db_sem=sem,
                                        )
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
                        logger.error(f"User {self} not found")
                        return

                    guild_list = []

                    for guild in user.guilds:
                        guild_list.append(
                            Guild(
                                guild.guild_id,
                                guild.guild_name,
                                guild.count_members,
                                guild.guild_sets,
                                db_guild=guild,
                            )
                        )

                    self._guilds = guild_list

                else:
                    query = select(Users).filter_by(ds_id=self._ds_id)
                    user = session.scalars(query).first()

                    if not user:
                        logger.error(f"User {self} not found")
                        return

                self.db_user = user
                self.username = user.username
                self.__updated_at = user.updated_at
                self.__created_at = user.created_at

                return self

            except Exception as e:
                logger.exception(f"Error when get info about user {self}", e)
                return None

    def update(self):
        with self._conn.Session() as session:
            try:
                user = select(Users).filter_by(ds_id=self.ds_id)
                user = session.scalars(user).first()

                if not user:
                    logger.error(f"User {self} not found")
                    return

                guilds_list = []
                if len(self.guilds) > 0:
                    for guild in self.guilds:
                        # if guild == self.guild_id:
                        #     continue
                        # overload?

                        guild = select(Guilds).filter_by(guild_id=guild.guild_id)
                        guild = session.scalars(guild).first()

                        if not guild:
                            logger.error(f"Guild {guild.guild_id} not found")
                            return

                        guilds_list.append(guild)

                if len(self.SEMs) > 0:
                    for sem in self.SEMs:
                        db_sem = select(Guild_User).where(
                            Guild_User.ds_id == self.ds_id,
                            Guild_User.guild_id == sem.guild.guild_id,
                        )
                        db_sem = session.scalars(db_sem).first()

                        if not db_sem:
                            logger.error(f"SEM for user {self} not found")
                            return

                        db_sem.scores = sem.scores
                        db_sem.experience = sem.experience
                        db_sem.messages = sem.messages

                user.username = self.username
                user.guilds = guilds_list

                session.commit()

            except Exception as e:
                logger.exception(f"Something went wrong when update user {self}", e)

    def add_relationship(self, guild_id: int):
        if guild_id in self.guilds:
            return

        with self._conn.Session() as session:
            try:
                query = select(Guilds).filter_by(guild_id=guild_id)
                guild = session.scalars(query).first()

                if not guild:
                    logger.error(f"Guild {self} not found")
                    return

            except Exception as e:
                logger.exception(f"Something went wrong when get guild {self}", e)
                return

        guild: Guild = Guild(
            guild_id, guild.guild_name, guild.count_members, guild.guild_sets, db_guild=guild
        )
        self.guilds.append(guild)

        return guild


class Guild:
    def __init__(
        self,
        guild_id: int,
        guild_name: str = None,
        count_members: int = None,
        guild_sets: dict = None,
        load_users: bool = False,
        load_tops: bool = False,
        load_limit: int = 20,
        db_guild: Guilds = None,
    ):
        self._guild_id: int = guild_id
        self._guild_name: str | None = guild_name
        self._count_members: int | None = count_members
        self._guild_sets: dict | None = guild_sets
        self._db_guild: Guilds | None = db_guild
        self._top_scores: list[User] | None = None
        self._top_messages: list[User] | None = None

        self._users: list[User] | None = None
        self._SEMs: list[SEM] | None = None

        self.__created_at: datetime | None = None
        self.__updated_at: datetime | None = None

        self._conn: DBConnection = DBConnection()
        self._enc: JsonEncoder = JsonEncoder()

        self._load_tops: bool = load_tops
        self._load_users: bool = load_users or self._load_tops
        self._load_limit: int = load_limit

        self.add()

    def __del__(self):
        self.update()

    def __eq__(self, other):
        return self.guild_id == other.guild_id

    def __repr__(self) -> str:
        return f"<Guild {self.guild_name}, {self.guild_id}>"

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
    def guild_sets(self) -> dict:
        """Settings of Guild"""

        if isinstance(self._guild_sets, dict):
            return self._guild_sets

        elif isinstance(self._guild_sets, str):
            return self._enc.code_from_json(self._guild_sets)

        else:
            return None

    @guild_sets.setter
    def guild_sets(self, new_guild_sets: dict | str):
        if isinstance(new_guild_sets, dict):
            self._guild_sets = self._enc.code_to_json(new_guild_sets)

        elif isinstance(new_guild_sets, str):
            self._guild_sets = new_guild_sets

        else:
            raise AttributeError("Guild sets must be dict or str type")

    @property
    def created_at(self) -> datetime:
        """Record creation time"""
        return self.__created_at

    @property
    def updated_at(self) -> datetime:
        """Record update time"""
        return self.__updated_at

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, new_users: list[User]):
        self._users = new_users

    @property
    def SEMs(self):
        return self._SEMs

    @SEMs.setter
    def SEMs(self, new_sems: [SEMs]):
        self._SEMs = new_sems

    @property
    def top_scores(self):
        return self._top_scores

    @top_scores.setter
    def top_scores(self, new_top_scores: list[SEMs]):
        self._top_scores = new_top_scores

    @property
    def top_messages(self):
        return self._top_scores

    @top_messages.setter
    def top_messages(self, new_top_messages: list[SEMs]):
        self._top_scores = new_top_messages

    @property
    def db_guild(self) -> Guilds:
        """DB Guilds model"""
        return self._db_guild

    @db_guild.setter
    def db_guild(self, new_db_guild) -> Guilds:
        self._db_guild = new_db_guild

    def add(self):
        with self._conn.Session() as session:
            try:
                guild = Guilds(
                    guild_id=self.guild_id,
                    guild_name=self.guild_name,
                    count_members=self.count_members,
                )

                session.add(guild)
                session.commit()

                self.guild_id = guild.guild_id
                self.guild_name = guild.guild_name
                self._count_members = guild.count_members
                self.guild_sets = guild.guild_sets
                self.__created_at = guild.created_at
                self.__updated_at = guild.updated_at

            except IntegrityError:
                session.rollback()
                guild = self.load()
                if guild is not None:
                    logger.debug(f"Guild {self} already in database")
                else:
                    logger.exception(
                        f"Something went wrong when get guild {self} for add function\n",
                        IntegrityError,
                    )

            except Exception as e:
                logger.exception(f"Something went wrong when add guild {self}", e)
                return

    def load(self):

        with self._conn.Session() as session:
            try:
                if self._load_tops:
                    query = (
                        select(Guilds)
                        .options(selectinload(Guilds.users))
                        .filter_by(guild_id=self.guild_id)
                    )

                    query_scm = select(Guild_User).filter_by(guild_id=self.guild_id)

                    sem_res: list[Guild_User] = session.scalars(query_scm).all()
                    guild: Guilds = session.scalars(query).first()

                    if not guild or sem_res is None:
                        logger.error(f"Guild {self} or sem not found")
                        return

                    users_list = []
                    SEMs_list = []

                    if guild.users is not None:
                        for user in guild.users:
                            for sem in sem_res:
                                if user.ds_id == sem.ds_id:
                                    user = User(
                                        ds_id=user.ds_id,
                                        username=user.username,
                                        db_user=user,
                                    )
                                    users_list.append(user)
                                    SEMs_list.append(
                                        SEM(
                                            user=user,
                                            scores=sem.scores,
                                            experience=sem.experience,
                                            messages=sem.messages,
                                            db_sem=sem,
                                        )
                                    )

                    self.users = users_list
                    self.SEMs = SEMs_list
                    self.top_scores = sorted(self.SEMs, key=lambda x: x.scores, reverse=True)
                    self.top_messages = sorted(self.SEMs, key=lambda x: x.messages, reverse=True)

                    if len(self.top_scores) > self._load_limit:
                        self.top_scores = self.top_scores[: self._load_limit]

                    if len(self.top_messages) > self._load_limit:
                        self.top_messages = self.top_messages[: self._load_limit]

                elif self._load_users:
                    query = (
                        select(Guilds)
                        .options(selectinload(Guilds.users))
                        .filter_by(guild_id=self.guild_id)
                    )

                    guild: Guilds = session.scalars(query).first()

                    if not guild:
                        logger.error(f"Can't find guild {self}")
                        return

                    if guild.users is not None:
                        users_list = []
                        for u in guild.users:
                            users_list.append(User(ds_id=u.ds_id, username=u.username, db_user=u))

                        print()

                        self.users = users_list

                else:
                    query = select(Guilds).filter_by(guild_id=self.guild_id)

                    guild = session.scalars(query).first()

                    if not guild:
                        logger.error(f"Can't find guild {self}")
                        return

                self.guild_name = guild.guild_name
                self.count_members = guild.count_members
                self.guild_sets = guild.guild_sets
                self.__created_at = guild.created_at
                self.__updated_at = guild.updated_at

                return self

            except Exception as e:
                logger.exception(f"Something went wrong when get guild {self}", e)

    def update(self):
        with self._conn.Session() as session:
            try:
                guild = select(Guilds).filter_by(guild_id=self.guild_id)
                guild = session.scalars(guild).first()

                if guild is None:
                    logger.error(f"Error was occurred when update guild {self}")
                    return

                guild.guild_name = self.guild_name
                guild.guild_sets = self._enc.code_to_json(self.guild_sets)
                guild.count_members = self.count_members

                session.commit()

            except Exception as e:
                logger.exception(f"Something went wrong when update guild {self}", e)


class SEM:
    def __init__(
        self,
        guild: Guild = None,
        user: User = None,
        scores: int = 0,
        experience: int = 0,
        messages: int = 0,
        db_sem: Guild_User = None,
    ):
        self._scores: int = scores
        self._experience: int = experience
        self._messages: int = messages
        self._guild: Guild | None = guild
        self._user: User | None = user
        self._db_sem: Guild_User | None = db_sem

    def __eq__(self, other):
        return (
            self.guild.guild_id == other.guild.guild_id
            if self.user is None
            else self.user.ds_id == other.user.ds_id
        )

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
    def user(self):
        """User for THIS SEM"""
        return self._user

    @property
    def db_sem(self) -> Guild_User | None:
        """DB record about scores, exp and messages"""
        return self._db_sem
