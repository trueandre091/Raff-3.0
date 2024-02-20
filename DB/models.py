from typing import Annotated
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from DB.JSONEnc import JsonEncoder
from DB.config_default import GUILD_CONFIG

intid = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    """Base class for inheritance new models"""

    repr_cols_num = 1
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

    repr_cols_num = 5

    ds_id: Mapped[int] = mapped_column(ForeignKey("users.ds_id"), primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.guild_id"), primary_key=True)

    experience: Mapped[int] = mapped_column(default=0)
    scores: Mapped[int] = mapped_column(default=0)

    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class Users(Base):
    """Users model for database"""

    __tablename__ = "users"
    repr_cols = ("username",)
    repr_cols_num = 0

    ds_id: Mapped[intid]
    username: Mapped[str]
    # experience: Mapped[int] = mapped_column(default=0)
    # scores: Mapped[int] = mapped_column(default=0)
    messages: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    guilds: Mapped[list["Guilds"]] = relationship(back_populates="users", secondary="guild_user")


class Guilds(Base):
    """Guilds model for database"""

    __tablename__ = "guilds"
    repr_cols = ("guild_name", )
    repr_cols_num = 0

    guild_id: Mapped[intid]
    guild_name: Mapped[str]
    count_members: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    guild_sets: Mapped[str] = mapped_column(default=JsonEncoder.code_to_json(GUILD_CONFIG))

    users: Mapped[list["Users"]] = relationship(back_populates="guilds", secondary="guild_user")


if __name__ == "__main__":
    engine = create_engine("sqlite:///DataBase.db", echo=True)
    # Guild_User.__table__.drop(engine)
    # Users.__table__.drop(engine)
    # Guilds.__table__.drop(engine)
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
