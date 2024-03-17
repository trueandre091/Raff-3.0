import time
import asyncio
from DataBaseNew import User, Guild


def users_tests():
    user1 = User(520600815535128587, guild_id=1189637072030531695, load_sem=True)
    # print(user1)
    # user2 = User(529291000418402314, load_guilds=True)
    # user3 = User(797035045985452032)

    # print(user1.SEMs)

    # for sem in user1.SEMs:
    #     if sem.guild.guild_id == 1189637072030531695:
    #         sem.scores = 634
    #         sem.experience = 8876
    #         sem.messages = 871


def guilds_test():
    guild = Guild(1189637072030531695)
    guild.guild_name = "Тест1"
    # print(guild.guild_sets)
    # print(guild)
    # guild.update()


async def main():
    users_tests()
    # guilds_test()


if __name__ == "__main__":
    s = time.perf_counter()
    asyncio.run(main())
    f = time.perf_counter()
    print(f"Total script time: {f - s}")
