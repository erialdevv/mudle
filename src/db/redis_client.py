import redis.asyncio as redis
from db.config import RedisConfig

redis_client=redis.from_url(
    RedisConfig.redis_url, 
    encoding="utf-8",
    decode_responses=True
)

async def get_redis()->redis.Redis:
    return redis_client