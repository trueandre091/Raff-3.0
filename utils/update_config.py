import asyncio
from new_config import GUILD_CONFIG
from DB.DataBase import GuildsDBase
from DB.JSONEnc import JsonEncoder
from loguru import logger


async def update_all_configs(config, guild_config):
    config = config
    guild_config = guild_config

    for key in config.keys():
        try:
            if isinstance(config[key], dict):
                await update_all_configs(
                    config.get(key, "ISN't HERE"), guild_config.get(key, "ISN't HERE")
                )
            else:
                if key == "ADDING_REACTIONS_THREADS_SETTINGS":
                    config[key] = guild_config.get(key, dict())

                elif key == "COLOR":
                    config[key] = guild_config.get(key)

                config[key] = guild_config.get(key, config[key])
                logger.info(f"Successfully updated {key}")
        except Exception as e:
            logger.exception(f"Error when update config by key {key}", e)
            return False

    return config


async def main():
    gdb: GuildsDBase = GuildsDBase()
    enc: JsonEncoder = JsonEncoder()
    guilds = await gdb.get_all_guilds()
    if guilds:
        to_update = []
        for guild in guilds:
            guild_config = enc.code_from_json(guild.guild_sets)
            print(guild.guild_name)
            res = await update_all_configs(GUILD_CONFIG, guild_config)
            if res:
                to_update.append({"guild_id": guild.guild_id, "guild_sets": res})
            else:
                logger.error(f"Error when update guild {guild.guild_name}")

        await gdb.update_guild(to_update)


if __name__ == "__main__":
    # logger.remove()
    logger.add(
        "logs.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
        level="DEBUG",
        rotation="1 week",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    asyncio.run(main())
