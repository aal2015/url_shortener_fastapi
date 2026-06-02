import json
import time

from fastapi import Depends, HTTPException, Request
import redis

from database import get_redis

CAPACITY = 10           # max tokens
REFILL_RATE = 1 / 6     # 1 token every 6 seconds


def token_bucket_limiter(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis)
):
    ip = request.client.host

    key = f"bucket:{ip}"

    now = time.time()

    bucket_data = redis_client.get(key)

    if bucket_data is None:

        bucket = {
            "tokens": CAPACITY,
            "last_refill": now
        }

    else:

        bucket = json.loads(bucket_data)

    # Refill tokens
    elapsed = now - bucket["last_refill"]

    bucket["tokens"] = min(
        CAPACITY,
        bucket["tokens"] + elapsed * REFILL_RATE
    )

    bucket["last_refill"] = now

    # Reject if empty
    if bucket["tokens"] < 1:

        redis_client.set(
            key,
            json.dumps(bucket),
            ex=3600
        )

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    # Consume token
    bucket["tokens"] -= 1

    redis_client.set(
        key,
        json.dumps(bucket),
        ex=3600
    )