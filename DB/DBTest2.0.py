import asyncio
from DataBaseNew import User


async def main():
    user1 = User(520600815535128587, load_sem=True)
    user2 = User(529291000418402314, load=False)
    user3 = User(797035045985452032)
    # await asyncio.sleep(3)
    # await user1.load_info(True, True)
    print(user1.username)


if __name__ == "__main__":
    asyncio.run(main())
