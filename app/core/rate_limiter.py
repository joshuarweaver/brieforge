"""Rate limiter supporting Redis with in-memory fallback."""
import time
import uuid
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, DefaultDict

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


class RateLimitExceeded(Exception):
    """Raised when a caller exceeds the configured rate limit."""

    def __init__(self, retry_after: float):
        super().__init__("Rate limit exceeded")
        self.retry_after = retry_after


class BaseRateLimiter:
    """Interface for rate limit backends."""

    def check(self, key: str, limit: int, window_seconds: int) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class InMemoryRateLimiter(BaseRateLimiter):
    """Token bucket limiter backed by process memory."""

    def __init__(self) -> None:
        self._hits: DefaultDict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        with self._lock:
            bucket = self._hits[key]
            threshold = now - window_seconds

            while bucket and bucket[0] <= threshold:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = window_seconds - (now - bucket[0])
                raise RateLimitExceeded(max(retry_after, 0.0))

            bucket.append(now)


class RedisRateLimiter(BaseRateLimiter):
    """Distributed rate limiter backed by Redis sorted sets."""

    _SCRIPT = """
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local member = ARGV[4]

    redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
    local count = redis.call('ZCARD', key)

    if count >= limit then
        local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
        local retry_after = 0

        if #oldest > 0 then
            retry_after = window - (now - tonumber(oldest[2]))
            if retry_after < 0 then
                retry_after = 0
            end
        end

        return {0, retry_after}
    end

    redis.call('ZADD', key, now, member)
    redis.call('EXPIRE', key, window)

    return {1, 0}
    """

    def __init__(self, client: Redis) -> None:
        self.client = client
        self._script = client.register_script(self._SCRIPT)

    @staticmethod
    def _key(key: str) -> str:
        return f"rate:{key}"

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex}"

        allowed, retry_after = self._script(
            keys=[self._key(key)],
            args=[limit, window_seconds, now, member],
        )

        if isinstance(allowed, (bytes, bytearray)):
            allowed = int(allowed.decode())
        elif isinstance(allowed, str):
            allowed = int(allowed)

        if isinstance(retry_after, (bytes, bytearray)):
            retry_after = float(retry_after.decode())
        elif isinstance(retry_after, str):
            retry_after = float(retry_after)

        if not allowed:
            raise RateLimitExceeded(float(retry_after))


def _create_rate_limiter() -> BaseRateLimiter:
    redis_url = settings.RATE_LIMIT_REDIS_URL
    if redis_url:
        try:
            client = Redis.from_url(redis_url, decode_responses=False)
            client.ping()
            return RedisRateLimiter(client)
        except RedisError:
            # Fall back to in-memory limiter if Redis is unavailable
            pass
    return InMemoryRateLimiter()


rate_limiter: BaseRateLimiter = _create_rate_limiter()
