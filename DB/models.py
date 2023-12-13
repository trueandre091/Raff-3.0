from typing import Annotated
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from JSONEnc import JsonEncoder
from config_default import GUILD_CONFIG

intid = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class Guild_User(Base):
    __tablename__ = "guild_user"

    id: Mapped[intid]
    disc_id: Mapped[int] = mapped_column(ForeignKey("users.disc_id"))
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.guild_id"))

    # id = Column(Integer, primary_key=True)
    # disc_id = Column(Integer, ForeignKey("users.disc_id"))
    # guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    # extra_info = Column(Text)

    def __repr__(self) -> str:
        return f"id={self.id!r}, disc_id={self.disc_id!r}, guild_id={self.guild_id!r}"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[intid]
    username: Mapped[str]
    disc_id: Mapped[int]
    experience: Mapped[int] = mapped_column(default=0)
    scores: Mapped[int] = mapped_column(default=10)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow(), onupdate=datetime.utcnow)
    guilds: Mapped["Guild_User"] = relationship(backref='user')

    # id = Column(Integer, primary_key=True)
    # username = Column(String(30), nullable=False)
    # disc_id = Column(Integer, nullable=False)
    # experience = Column(Integer, nullable=False, default=0)
    # scores = Column(Integer, nullable=False, default=10)
    # guilds = relationship("Guild_User", backref='user')

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, disc_id={self.disc_id!r}"


class Guilds(Base):
    __tablename__ = "guilds"

    id: Mapped[intid]
    guild_id: Mapped[int]
    guild_name: Mapped[str]
    count_members: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    guild_sets: Mapped[str] = mapped_column(default=JsonEncoder.code_to_json(GUILD_CONFIG))

    # id = Column(Integer, primary_key=True)
    # guild_id = Column(Integer, nullable=False)
    # guild_name = Column(String(30), nullable=False)
    # count_of_members = Column(Integer, nullable=False)
    # guild_settings = Column(Text, nullable=False, default=lambda x: await JsonEncoder.code_to_json(GUILD_CONFIG))
    # users = relationship("Guild_User", backref="guild")

    def __repr__(self) -> str:
        return f"id={self.id!r}, guild_id={self.guild_id!r}, guild_name={self.guild_name!r}"


if __name__ == "__main__":
    engine = create_engine("sqlite:///DataBase.db", echo=True)
    Base.metadata.create_all(engine)

    res = JsonEncoder.code_to_json(GUILD_CONFIG)

    print(res)
