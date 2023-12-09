"""Class for code and decode json arrays for guild settings"""
import json


class JsonEncoder:
    """Code and decode settings for Guilds"""

    @staticmethod
    async def code_to_json(data):
        return json.dumps(data)

    @staticmethod
    async def code_from_json(data):
        return json.loads(data)
