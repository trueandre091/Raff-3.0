import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from DB.models import Users, Guild_User


def main(eng):
    with Session(eng) as session:
        users = select(Users)
        users = session.scalars(users).all()

        guild_user = select(Guild_User)
        guild_user = session.scalars(guild_user).all()

        for user in users:
            for rec in guild_user:
                if user.ds_id == rec.ds_id:
                    rec.scores = user.scores
                    rec.experience = user.experience

        session.commit()


if __name__ == "__main__":
    engine = create_engine("sqlite:///../../DB/DataBase.db", echo=True)
    main(engine)
