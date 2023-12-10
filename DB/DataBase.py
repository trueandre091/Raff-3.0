"""Start of create DB!"""
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Users, Guilds


class DataBase:
    """Class for creating connection to database and managing it"""

    def __init__(self):
        try:
            self.engine = create_async_engine("sqlite:///DataBase.db", echo=True)
            self.session = self.get_session(self.engine)
        except:
            raise "Error creating an engine or connecting to database"

    @staticmethod
    def get_session(engine):
        session = async_sessionmaker(engine)
        async with session() as session:
            return session

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

    async def add_user(self, args: dict) -> Union[True, False]:
        data = args
        try:
            user = Users(username=data["username"], disc_id=data["disc_id"])
            self.session.add(user)
            return True
        except:
            print("Something went wrong then adding user", data["username"], data["disc_id"])

        return False

    async def add_guild(self, args) -> Union[True, False]:
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

    async def update_user(self, args) -> Union[True, False]:
        pass

    async def update_guild(self, args) -> Union[True, False]:
        pass
