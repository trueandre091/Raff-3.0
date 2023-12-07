"""Start of create DB!"""
import sqlalchemy as sa
from sqlalchemy import create_engine

engine = create_engine("sqlite:///DataBase.db")

connection = engine.connect()

metadata = sa.MetaData()