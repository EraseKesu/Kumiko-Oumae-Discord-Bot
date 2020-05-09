import asyncpg
from asyncpg.pool import Pool, create_pool
from typing import Optional


class Database:
    pool: Optional[Pool] = None

    @classmethod
    async def connect(cls) -> None:
        cls.pool = await create_pool(user="postgres")

    @classmethod
    async def execute(cls, execute_string, *args):
        async with cls.pool.acquire() as db:
            return await db.execute(execute_string, *args)

    @classmethod
    async def fetch_row(cls, query_string, *args):
        async with cls.pool.acquire() as db:
            return await db.fetchrow(query_string, *args)

    @classmethod
    async def fetch(cls, query_string, *args):
        async with cls.pool.acquire() as db:
            return await db.fetch(query_string, *args)

    @classmethod
    async def close(cls):
        await cls.pool.close()
