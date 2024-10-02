import os
import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from typing import Optional


class RedisManager:
    """
    Redis manager class to handle Redis connections and job status management

    :cvar _pool: Redis connection pool
    :cvar _settings: Redis connection settings
    """

    _pool = None
    _settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        database=int(os.getenv("REDIS_DB", 2)),
        conn_timeout=300,
        max_connections=10,
    )

    @classmethod
    async def get_pool(cls):
        if cls._pool is None or not await cls._check_connection():
            cls._pool = await cls._reconnect()
        return cls._pool

    @classmethod
    async def _check_connection(cls):
        try:
            await cls._pool.ping()
            return True
        except (OSError, ConnectionError):
            return False

    @classmethod
    async def _reconnect(cls):
        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            try:
                return await create_pool(cls._settings)
            except (OSError, ConnectionError):
                attempt += 1
                await asyncio.sleep(1)
        raise ConnectionError("Failed to reconnect to Redis after several attempts.")

    @classmethod
    async def set_job_status(cls, call_id: str, status: str):
        redis = await cls.get_pool()
        await redis.set(f"job_status:{call_id}", status, ex=3600)

    @classmethod
    async def get_job_status(cls, call_id: str) -> Optional[str]:
        redis = await cls.get_pool()
        status = await redis.get(f"job_status:{call_id}")
        if status is not None:
            return status.decode("utf-8")
        return None

    @classmethod
    async def delete_job_status(cls, call_id: str):
        redis = await cls.get_pool()
        await redis.delete(f"job_status:{call_id}")

    @classmethod
    async def delete_all_jobs(cls):
        redis = await cls.get_pool()
        keys = await redis.keys("job_status:*")
        if keys:
            await redis.delete(*keys)
