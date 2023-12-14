"""Database Management"""
import asyncio
from typing import Union
import traceback

from sqlalchemy import select, update
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

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
