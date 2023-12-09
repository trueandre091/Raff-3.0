"""Start of create DB!"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine("sqlite:///DataBase.db", echo=True)

Base = declarative_base()


class Guild_User(Base):
    __tablename__ = "guild_users"

    id = Column(Integer, primary_key=True)
    disc_id = Column(Integer, ForeignKey("users.disc_id"))
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    extra_info = Column(Text)

    def __repr__(self) -> str:
        return f"id={self.id!r}, disc_id={self.disc_id!r}, guild_id={self.guild_id!r}, extra_info={self.extra_info!r}"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False)
    disc_id = Column(Integer, nullable=False)
    guilds = relationship("Guild_User", backref='user')

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, disc_id={self.disc_id!r}"


class Guilds(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, nullable=False)
    servname = Column(String(30), nullable=False)
    count_of_members = Column(Integer, nullable=False)
    users = relationship("Guild_User", backref="guild")


Base.metadata.create_all(engine)