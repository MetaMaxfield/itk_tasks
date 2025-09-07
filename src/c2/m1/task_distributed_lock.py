import datetime
import logging
import os
import socket
import time
from multiprocessing import Process
from typing import Any

import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

hostname = socket.gethostname()
pid = os.getpid()

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def single(max_processing_time: datetime.timedelta) -> callable:
    def decorator(func: callable):
        def wrapper(*args: Any, **kwargs: Any) -> callable:
            key = f"{func.__module__}:{func.__qualname__}"
            value = f"{hostname}:{pid}"
            sec_max_processing_time = int(max_processing_time.total_seconds())

            if r.set(name=key, ex=sec_max_processing_time, value=value, nx=True):
                # блок try-finally на случай если в func вызовется ошибка...
                # ...и задача останется висеть в БД
                try:
                    start_time = time.perf_counter()
                    result = func(*args, **kwargs)
                    duration = time.perf_counter() - start_time

                    # если время выполнения "max_processing_time" установлено...
                    # ...некорректно
                    if duration > sec_max_processing_time:
                        logging.error(
                            (
                                f"Execution of {key} exceeded max_processing_time by "
                                f"{(duration - sec_max_processing_time):.2f}s"
                            )
                        )

                    return result

                finally:
                    r.delete(key)

            else:
                logging.warning(f"{key} is already running on {r.get(key)}")

        return wrapper

    return decorator


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction1():
    time.sleep(2)


@single(max_processing_time=datetime.timedelta(seconds=2))
def process_transaction2():
    time.sleep(5)


if __name__ == "__main__":
    # Стандартный вариант с попыткой параллельного запуска
    processes = [Process(target=process_transaction1) for _ in range(3)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()

    # Вариант с неправильно выбранным максимальным временем выполнения
    processes = [Process(target=process_transaction2) for _ in range(3)]
    for process in processes:
        process.start()
        time.sleep(2)
    for process in processes:
        process.join()
