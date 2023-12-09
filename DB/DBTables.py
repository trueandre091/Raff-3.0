"""Start of create DB!"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from DataBase import JsonEncoder
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


class User(Base):
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
    guild_settings = Column(Text, nullable=False, default=JsonEncoder.code_to_json(GUILD_CONFIG))
    users = relationship("Guild_User", backref="guild")

    def __repr__(self) -> str:
        return f"id={self.id!r}, guild_id={self.guild_id!r}, guild_name={self.guild_name!r}, count_of_members={self.count_of_members!r}, guild_settings={self.guild_settings!r}"


if __name__ == "__main__":
    Base.metadata.create_all(engine)
else:
    raise "This module only for creating tables!"
