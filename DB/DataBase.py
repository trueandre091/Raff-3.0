"""Database Management"""

import asyncio
from typing import Union
import traceback

from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

    async def add_user(self, data: dict) -> Union[Users, None]:
        with self.Session() as session:
            try:
                user = Users(username=data["username"], disc_id=data["disc_id"])

                session.add(user)
                session.commit()

                return user
            except Exception:
                print("Something went wrong then adding user")
                print(traceback.format_exc())

        return

    @staticmethod
    def get_user_static(session, data):
        try:
            if "disc_id" in data.keys():
                user = select(Users).filter_by(disc_id=data["disc_id"])
                user = session.scalars(user).first()
                if not user:
                    print("Can't find user by discord id in database")
                    return

                return user

            elif "username" in data.keys():
                user = select(Users).filter_by(username=data["username"])
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
        with self.Session() as session:
            return self.get_user_static(session, data)

    async def update_user(self, data: dict) -> Union[Users, None]:
        with self.Session() as session:
            user = self.get_user_static(session, data)
            try:
                user.username = lambda _: user.username if not data.get("username") else data["username"]
                user.scores = lambda _: user.username if not data.get("scores") else data["scores"]
                user.experience = lambda _: user.username if not data.get("experience") else data["experience"]

                session.commit()

                return user

            except Exception:
                print("Something went wrong when update user")
                print(traceback.format_exc())

        return

    ####################################   GUILDS   ############################################

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

    async def add_relationship(self):
        pass

    async def delete_relationship(self):
        pass


async def test_add_user():
    db = DataBase(echo=True)

    data = {"username": "TopNik_",
            "disc_id": 785364734786}

    res = await db.add_user(data)

    print(res)


async def test_add_guild():
    db = DataBase(echo=True)

    data = {"guild_id": 874365893234,
            "guild_name": "Homey Temple"}

    res = await db.add_guild(data)

    print(res)


async def main():
    await test_add_guild()
    await test_add_guild()


if __name__ == "__main__":
    engine = create_engine("sqlite:///DataBase.db", echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    asyncio.run(main())
