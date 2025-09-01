import asyncio
import json

import aiohttp

FILE_NAME = "result.jsonl"


def read_file(file_path: str):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()


async def create_request(url: str, session: aiohttp.ClientSession) -> tuple[str, int]:
    try:
        async with session.get(
            url, timeout=300
        ) as response:  # большой таймаут для тяжелых урлов
            status_code = response.status
            body = await response.json()
    except (aiohttp.ClientError, aiohttp.ServerTimeoutError):
        status_code = 0
        body = None

    if status_code == 200:
        write_to_file(url, body)  # сразу пишу в файл, чтобы не нагружать память


def write_to_file(url, content):
    with open(FILE_NAME, "a") as file:
        json_str = json.dumps({"url": url, "content": content}, ensure_ascii=False)
        file.write(f"{json_str}\n")


async def fetch_urls(file_path: str):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in read_file(file_path):
            task = asyncio.create_task(create_request(url, session))
            tasks.append(task)

            if len(tasks) == 5:  # вручную создаю по 5 асинхронных запросов
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:  # последние задачи если не кратны пяти
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    file = "./urls.txt"
    asyncio.run(fetch_urls(file))
