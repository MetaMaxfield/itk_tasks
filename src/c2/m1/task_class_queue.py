import pickle
import uuid
from typing import Any

import redis


class RedisQueue:
    """Use list in Redis."""

    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0
    r = redis.Redis(
        redis_host,
        redis_port,
        redis_db,
    )

    def __init__(self):
        self.key = str(uuid.uuid4())  # уникальный ключ для каждой очереди

    def publish(self, msg: Any) -> None:
        msg = pickle.dumps(msg)  # храню в виде байтовой строки для возможности...
        self.r.rpush(self.key, msg)  # ...добавления в очередь любого python-объекта

    def consume(self) -> Any | None:
        msg = self.r.lpop(self.key)
        return pickle.loads(msg) if msg else None


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
    assert q.consume() is None
