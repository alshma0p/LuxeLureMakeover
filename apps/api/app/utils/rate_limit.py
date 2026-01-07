import time
from typing import Dict
from redis import Redis

from app.core.config import settings


class RateLimiter:
    def __init__(self) -> None:
        self.limit = settings.rate_limit_per_minute
        self.window = 60
        self.store: Dict[str, list[float]] = {}
        self.redis = Redis.from_url(settings.redis_url) if settings.redis_url else None

    def allow(self, key: str) -> bool:
        now = time.time()
        if self.redis:
            pipeline = self.redis.pipeline()
            pipeline.zremrangebyscore(key, 0, now - self.window)
            pipeline.zadd(key, {str(now): now})
            pipeline.zcard(key)
            pipeline.expire(key, self.window)
            _, _, count, _ = pipeline.execute()
            return count <= self.limit
        timestamps = [ts for ts in self.store.get(key, []) if now - ts < self.window]
        timestamps.append(now)
        self.store[key] = timestamps
        return len(timestamps) <= self.limit


rate_limiter = RateLimiter()
