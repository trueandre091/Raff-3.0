from typing import Annotated
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from DB.JSONEnc import JsonEncoder
from DB.config_default import GUILD_CONFIG

intid = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    """Base class for inheritance new models"""
    repr_cols_num = 2
    repr_cols = tuple()

    def __repr__(self):
        """Relationships are not used in repr() because may lead to unexpected lazy loads"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Guild_User(Base):
    """Sheet for connect between Users and Guilds models"""

    __tablename__ = "guild_user"

    # id: Mapped[intid]

    disc_id: Mapped[int] = mapped_column(
        ForeignKey("users.disc_id", ondelete="CASCADE"),
        primary_key=True
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("guilds.guild_id", ondelete="CASCADE"),
        primary_key=True
    )

    # id = Column(Integer, primary_key=True)
    # disc_id = Column(Integer, ForeignKey("users.disc_id"))
    # guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    # extra_info = Column(Text)


class Users(Base):
    """Users model for database"""

    __tablename__ = "users"

    # id: Mapped[intid]
    disc_id: Mapped[intid]
    username: Mapped[str]
    experience: Mapped[int] = mapped_column(default=0)
    scores: Mapped[int] = mapped_column(default=10)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    guilds: Mapped[list["Guilds"]] = relationship(back_populates="users", secondary="guild_user")

    # guilds: Mapped["Guild_User"] = relationship(backref='user')
    # id = Column(Integer, primary_key=True)
    # username = Column(String(30), nullable=False)
    # disc_id = Column(Integer, nullable=False)
    # experience = Column(Integer, nullable=False, default=0)
    # scores = Column(Integer, nullable=False, default=10)
    # guilds = relationship("Guild_User", backref='user')


class Guilds(Base):
    """Guilds model for database"""
    __tablename__ = "guilds"

    # id: Mapped[intid]
    guild_id: Mapped[intid]
    guild_name: Mapped[str]
    count_members: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    guild_sets: Mapped[str] = mapped_column(default=JsonEncoder.code_to_json(GUILD_CONFIG))

    users: Mapped[list["Users"]] = relationship(back_populates="guilds", secondary="guild_user")

    # id = Column(Integer, primary_key=True)
    # guild_id = Column(Integer, nullable=False)
    # guild_name = Column(String(30), nullable=False)
    # count_of_members = Column(Integer, nullable=False)
    # guild_settings = Column(Text, nullable=False, default=lambda x: await JsonEncoder.code_to_json(GUILD_CONFIG))
    # users = relationship("Guild_User", backref="guild")


if __name__ == "__main__":
    engine = create_engine("sqlite:///DataBase.db", echo=True)
    Base.metadata.create_all(engine)

    res = JsonEncoder.code_to_json(GUILD_CONFIG)

    print(res)
