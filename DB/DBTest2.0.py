import asyncio
from DataBaseNew import User


async def main():
    user1 = User(520600815535128587, load_sem=True)
    user2 = User(529291000418402314, load_guilds=True)
    user3 = User(797035045985452032)
    # await asyncio.sleep(3)
    # await user1.load_info(True, True)

    # print(user1.SEMs)

    for sem in user1.SEMs:
        if sem.guild.guild_id == 1189637072030531695:
            sem.scores = 634
            sem.experience = 8876
            sem.messages = 871


if __name__ == "__main__":
    asyncio.run(main())
