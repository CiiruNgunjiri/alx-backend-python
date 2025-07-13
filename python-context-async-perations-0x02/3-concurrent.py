import asyncio
import aiosqlite

async def async_fetch_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return rows

async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            rows = await cursor.fetchall()
            return rows

async def fetch_concurrently():
    # Run both queries concurrently and wait for both to finish
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print("All users:")
    for user in all_users:
        print(user)
    print("\nUsers older than 40:")
    for user in older_users:
        print(user)

if __name__ == "__main__":
    asyncio.run(fetch_concurrently())

