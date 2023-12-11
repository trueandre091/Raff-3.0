"""Start of create DB!"""
import asyncio
from typing import Union

from sqlalchemy import select, update
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Users, Guilds, Base


class DataBase:
    """Class for creating connection to database and managing it"""

    def __init__(self):
        try:
            # self.engine = create_async_engine("sqlite:///DataBase.db", echo=True)
            # self.session = self.get_session(self.engine)
            self.engine = create_engine("sqlite:///DataBase.db", echo=True)
            self.Session = sessionmaker(self.engine)
        except:
            raise "Error creating an engine or connecting to database"

    # @staticmethod
    # def get_session(engine):
    #     session = async_sessionmaker(engine)
    #     async with session() as session:
    #         return session

    async def get_guild(self, id=None, guild_id=None, guild_name=None):
        with self.Session() as session:
            try:
                if id:
                    guilds_list = select(Guilds).filter_by(id=id)
                    guild = session.scalars(guilds_list).first()
                    if not guild:
                        print("Can't find guild by id in database")
                        return False

                    return guild

                elif guild_id:
                    guilds_list = select(Guilds).filter_by(guild_id=guild_id)
                    guild = session.scalars(guilds_list).first()
                    if not guild:
                        print("Can't find guild by guild_id in database")
                        return False

                    return guild

                elif guild_name:
                    guilds_list = select(Guilds).filter_by(guild_name=guild_name)
                    guild = session.scalars(guilds_list).first()
                    if not guild:
                        print("Can't find guild by guild_name in database")
                        return False

                    return guild

            except:
                print(
                    f"Something went wrong with get_guild method id: {id}, guild_id: {guild_id}, guild_name: {guild_name}")

        return False

    async def get_user(self, id=None, username=None, disc_id=None):
        with self.Session() as session:
            try:
                if id:
                    user_list = select(Users).filter_by(id=id)
                    user = session.scalars(user_list).first()
                    if not user:
                        print("Can't find user by id in database")
                        return False

                    return user

                elif username:
                    user_list = select(Users).filter_by(id=id)
                    user = session.scalars(user_list).first()
                    if not user:
                        print("Can't find user by id in database")
                        return False

                    return user

                elif disc_id:
                    user_list = select(Users).filter_by(id=id)
                    user = session.scalars(user_list).first()
                    if not user:
                        print("Can't find user by id in database")
                        return False

                    return user

            except:
                print(
                    f"Something went wrong with get_guild method id: {id}, guild_id: {username}, guild_name: {disc_id}")

        return False

    async def add_user(self, data: dict) -> Union[True, False]:
        with self.Session() as session:
            try:
                user = Users(username=data["username"], disc_id=data["disc_id"])

                session.add(user)
                session.commit()

                return True
            except:
                print("Something went wrong then adding user", data["username"], data["disc_id"])

        return False

    async def add_guild(self, data: dict) -> Union[True, False]:
        with self.Session() as session:
            try:
                guild = Guilds(guild_id=data["guild_id"], guild_name=data["guild_name"],
                               count_members=data["count_members"])

                session.add(guild)
                session.commit()

                return True
            except:
                print("Something went wrong then adding guild", data["guild_id"], data["guild_name"],
                      data["count_members"])

        return False

    async def update_user(self, data: dict) -> Union[True, False]:
        with self.Session() as session:
            try:
                session.execute(
                    update(Users)
                    .values(username=data["username"])
                    .filter_by(disc_id=data["disc_id"])
                )
                session.commit()

                return True

            except:
                print("Something went wrong when updating user", data["username"], data["disc_id"], data["experience"],
                      data["scores"])

        return False

    async def update_guild(self, data: dict) -> Union[True, False]:
        with self.Session() as session:
            try:
                updated_guild = Guilds(guild_id=data["guild_id"], guild_name=data["guild_name"],
                                       count_members=data["count_members"], guild_sets=data["guild_sets"])

                session.add(updated_guild)
                session.commit()

                return True

            except:
                print("Something went wrong when updating guild", data["guild_id"], data["guild_name"])

        return False


async def main():
    engine = create_engine("sqlite:///DataBase.db", echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = DataBase()

    user = {"username": "TopNik_",
            "disc_id": 8326758751}

    # loop = asyncio.get_event_loop()
    # res_u = loop.run_until_complete(db.add_user(data=user))

    res_u = await db.add_user(data=user)

    print("user", res_u)

    guild = {"guild_id": 907645237,
             "guild_name": "Homey Temple",
             "count_members": 3000}

    # loop = asyncio.get_event_loop()
    # res_g = loop.run_until_complete(db.add_guild(data=guild))

    res_g = await db.add_guild(guild)

    print("guild", res_g)

    update_user = {"username": "Nikita",
                   "disc_id": 8326758751,
                   "experience": 0,
                   "scores": 10}

    res_update_u = await db.update_user(update_user)

    print("Update user", res_update_u)


if __name__ == "__main__":
    asyncio.run(main())

    # engine = create_engine("sqlite:///DataBase.db", echo=True)
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    #
    # db = DataBase()
    #
    # user = {"username": "TopNik_",
    #         "disc_id": 8326758751}
    #
    # loop = asyncio.get_event_loop()
    # res_u = loop.run_until_complete(db.add_user(data=user))
    #
    # # res = await db.add_user(data=user)
    #
    # print("user", res_u)
    #
    # guild = {"guild_id": 907645237,
    #          "guild_name": "Homey Temple",
    #          "count_members": 3000}
    #
    # loop = asyncio.get_event_loop()
    # res_g = loop.run_until_complete(db.add_guild(data=guild))
    #
    # print("guild", res_g)
