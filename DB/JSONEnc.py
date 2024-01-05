"""Class for code and decode json arrays for guild settings"""
import json
from DB.config_default import GUILD_CONFIG


class JsonEncoder:
    """Code and decode settings for Guilds"""

    @staticmethod
    def code_to_json(data):
        return json.dumps(data)

    @staticmethod
    def code_from_json(data):
        return json.loads(data)

    @staticmethod
    def get_default_cfg():
        return json.dumps(GUILD_CONFIG)
