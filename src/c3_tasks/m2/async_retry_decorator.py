import asyncio
from functools import wraps


def async_retry(func=None, *, retries=1, exceptions):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cur_retr = 0
            while cur_retr < retries:
                try:
                    cur_retr += 1
                    return await func(*args, **kwargs)
                except exceptions:
                    print(f"Retrying {func.__name__} ({cur_retr}/{retries})...")
                    await asyncio.sleep(3)
            return await func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


@async_retry(retries=3, exceptions=(ValueError,))
async def unstable_task():
    print("Running task...")
    raise ValueError("Something went wrong")


async def main():
    try:
        await unstable_task()
    except Exception as e:
        print(f"Final failure: {e}")


if __name__ == "__main__":
    asyncio.run(main())
