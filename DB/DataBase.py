"""Methods and classes for working with database"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import json


class JsonEncoder:
    """Code and decode settings for Guilds"""

    @staticmethod
    def code_to_json(data):
        return json.dumps(data)

    @staticmethod
    def code_from_json(data):
        return json.loads(data)


class DataBase:
    """Class for creating connection to database and managing it"""
    def __init__(self):
        try:
            self.engine = create_engine("sqlite:///DataBase.db", echo=True)
            self.session = Session(self.engine)
        except:
            raise "Error creating an engine or connecting to database"




