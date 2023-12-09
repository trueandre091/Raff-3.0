"""Start of create DB!"""
from sqlalchemy import create_engine, select, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from JSONEnc import JsonEncoder
from config_default import GUILD_CONFIG

engine = create_engine("sqlite:///DataBase.db", echo=True)

Base = declarative_base()


class Guild_User(Base):
    __tablename__ = "guild_user"

    id = Column(Integer, primary_key=True)
    disc_id = Column(Integer, ForeignKey("users.disc_id"))
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    extra_info = Column(Text)

    def __repr__(self) -> str:
        return f"id={self.id!r}, disc_id={self.disc_id!r}, guild_id={self.guild_id!r}, extra_info={self.extra_info!r}"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False)
    disc_id = Column(Integer, nullable=False)
    experience = Column(Integer, nullable=False, default=0)
    scores = Column(Integer, nullable=False, default=10)
    guilds = relationship("Guild_User", backref='user')

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, disc_id={self.disc_id!r}, experience={self.experience!r}, scores={self.scores!r}, guilds={self.guilds!r}"


class Guilds(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, nullable=False)
    guild_name = Column(String(30), nullable=False)
    count_of_members = Column(Integer, nullable=False)
    guild_settings = Column(Text, nullable=False, default=lambda x: await JsonEncoder.code_to_json(GUILD_CONFIG))
    users = relationship("Guild_User", backref="guild")

    def __repr__(self) -> str:
        return f"id={self.id!r}, guild_id={self.guild_id!r}, guild_name={self.guild_name!r}, count_of_members={self.count_of_members!r}, guild_settings={self.guild_settings!r}"


class DataBase:
    """Class for creating connection to database and managing it"""

    def __init__(self):
        try:
            self.engine = create_engine("sqlite:///DataBase.db", echo=True)
            self.session = Session(self.engine)
        except:
            raise "Error creating an engine or connecting to database"

    async def get_guild(self, id=None, guild_id=None, guild_name=None):
        try:
            if id:
                guilds_list = select(Guilds).filter_by(id=id)
                guild = self.session.scalars(guilds_list).first()
                if not guild:
                    print("Can't find guild by id in database")
                    return False

                return guild

            elif guild_id:
                guilds_list = select(Guilds).filter_by(guild_id=guild_id)
                guild = self.session.scalars(guilds_list).first()
                if not guild:
                    print("Can't find guild by guild_id in database")
                    return False

                return guild

            elif guild_name:
                guilds_list = select(Guilds).filter_by(guild_name=guild_name)
                guild = self.session.scalars(guilds_list).first()
                if not guild:
                    print("Can't find guild by guild_name in database")
                    return False

                return guild

        except:
            print(
                f"Something went wrong with get_guild method id: {id}, guild_id: {guild_id}, guild_name: {guild_name}")

        return False

    async def get_user(self, id=None, username=None, disc_id=None):
        try:
            if id:
                user_list = select(Users).filter_by(id=id)
                user = self.session.scalars(user_list).first()
                if not user:
                    print("Can't find user by id in database")
                    return False

                return user

            elif username:
                user_list = select(Users).filter_by(id=id)
                user = self.session.scalars(user_list).first()
                if not user:
                    print("Can't find user by id in database")
                    return False

                return user

            elif disc_id:
                user_list = select(Users).filter_by(id=id)
                user = self.session.scalars(user_list).first()
                if not user:
                    print("Can't find user by id in database")
                    return False

                return user

        except:
            print(f"Something went wrong with get_guild method id: {id}, guild_id: {username}, guild_name: {disc_id}")

        return False

    async def add_user(self, args: dict) -> [True, False]:
        data = args
        try:
            user = Users(username=data["username"], disc_id=data["disc_id"])
            self.session.add(user)
            return True
        except:
            print("Something went wrong then adding user", data["username"], data["disc_id"])

        return False

    async def add_guild(self, args) -> [True, False]:
        data = args
        try:
            guild = Guilds(guild_id=data["guild_id"], guild_name=data["guild_name"],
                           count_of_members=data["count_of_members"])
            self.session.add(guild)
            return True
        except:
            print("Something went wrong then adding guild", data["guild_id"], data["guild_name"],
                  data["count_of_members"])

        return False

    async def update_user(self, args) -> [True, False]:
        pass

    async def update_guild(self, args) -> [True, False]:
        pass


if __name__ == "__main__":
    Base.metadata.create_all(engine)
