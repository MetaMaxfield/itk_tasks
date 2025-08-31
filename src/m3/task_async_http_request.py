import asyncio
import json

import aiohttp

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]

sem = asyncio.Semaphore(5)


async def create_request(url: str, session: aiohttp.ClientSession) -> tuple[str, int]:
    async with sem:
        try:
            async with session.get(url, timeout=10) as response:
                status_code = response.status
        except (aiohttp.ClientError, aiohttp.ServerTimeoutError):
            status_code = 0
    return url, status_code


async def fetch_urls(urls: list[str], file_path: str) -> dict[str, int]:
    tasks = []

    # создаём асинхронные задачи
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(create_request(url, session))
        results = await asyncio.gather(*tasks)

    results = {url: status_code for url, status_code in results}

    # создаём файл (синхронно, т.к. в условии нет aiofiles)
    with open(file_path, "w") as file:
        for key, value in results.items():
            json_str = json.dumps({"url": key, "status_code": value})
            file.write(f"{json_str}\n")

    return results


if __name__ == "__main__":
    res = asyncio.run(fetch_urls(urls, "./results.jsonl"))
    print(res)
