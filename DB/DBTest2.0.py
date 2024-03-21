import time
from DataBaseNew import UserDBase, GuildDBase


def users_tests():
    guild = guilds_test()
    user1 = UserDBase(520600815535128587, 520600815535128587, guild=guild, load_sem=True)
    print(user1.SEMs)
    for SEM in user1.SEMs:
        if SEM == guild:
            print("True")
    # user2 = User(529291000418402314, load_guilds=True)
    # user3 = User(797035045985452032)

    # print(user1.SEMs)

    # for sem in user1.SEMs:
    #     if sem.guild.guild_id == 1189637072030531695:
    #         sem.scores = 634
    #         sem.experience = 8876
    #         sem.messages = 871


def guilds_test():
    guild = GuildDBase(1189637072030531695, "Тест1", 2, load_tops=True)
    print(guild)
    # guild.guild_name = "Тест1"
    # print(guild.guild_sets)
    # print(guild)
    # guild.update()

    return guild


def main():
    # users_tests()
    guilds_test()


if __name__ == "__main__":
    s = time.perf_counter()
    main()
    f = time.perf_counter()
    print(f"Total script time: {f - s}")
