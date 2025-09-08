import random
import time
import redis
import uuid
import time


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    """Use sorted set (sliding window principle)."""
    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0
    r = redis.Redis(
        redis_host,
        redis_port,
        redis_db,
    )
    
    def __init__(self):
        # уникальный ключ для каждого объекта лимиттера
        self.key = str(uuid.uuid4())
    
    def test(self) -> bool:
        score =  int(time.time()) * 1000  # число для сортировки (время в милисекундах)
        limit_score = score - 3000
        
        # удаляем просрочиевшееся 
        self.r.zremrangebyscore(self.key, 0, limit_score)
        if self.r.zcard(self.key) >= 5:
            return False
        
        value = str(uuid.uuid4())  # уникальное значение для каждого запроса
        self.r.zadd(self.key, {value: score})
        return True
    

def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == '__main__':
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(0, 2))  # изменил на (0, 2) для большей наглядности
        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")

