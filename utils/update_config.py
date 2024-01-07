import asyncio
from new_config import GUILD_CONFIG
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder
from loguru import logger

logger.add(
    "logs.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
    level="DEBUG",
    rotation="1 week",
    compression="zip",
    backtrace=True,
    diagnose=True,
)


async def update_all_configs(config, guild_config):
    config = config
    guild_config = guild_config

    for key in config.keys():
        try:
            # print(key)
            if isinstance(config[key], dict):
                await update_all_configs(
                    config.get(key, "ISN't HERE"), guild_config.get(key, "ISN't HERE")
                )
            else:
                if key == "ADDING_REACTIONS_THREADS_SETTINGS":
                    config[key] = guild_config.get(key, dict())

                elif key == "COLOR":
                    print(type(guild_config[key]), type(int(hex(guild_config[key]), 16)))
                    config[key] = guild_config.get(key)

                config[key] = guild_config.get(key, config[key])
                # print(key, guild_config.get(key, "ISN't HERE"), sep="--------")
            logger.info(f"Successfully updated {key}")
        except Exception as e:
            logger.exception(f"Error when update config by key {key}", e)

    return config


async def main():
    gdb: GuildsDBase = GuildsDBase()
    enc: JsonEncoder = JsonEncoder()
    guilds = await gdb.get_all_guilds()
    if guilds:
        for guild in guilds:
            guild_config = enc.code_from_json(guild.guild_sets)
            print(guild.guild_name)
            res = await update_all_configs(GUILD_CONFIG, guild_config)
            print(res)
            print("\n\n\n\n\n\n\n")


if __name__ == "__main__":
    asyncio.run(main())
