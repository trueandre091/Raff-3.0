"""Class for code and decode json arrays for guild settings"""
import json


class JsonEncoder:
    """Code and decode settings for Guilds"""

    @staticmethod
    def code_to_json(data):
        return json.dumps(data)

    @staticmethod
    def code_from_json(data):
        return json.loads(data)
