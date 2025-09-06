import asyncio
import json
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import AsyncGenerator

import aiofiles
import aiohttp

OUTPUT_FILE = "result.jsonl"

executor = ProcessPoolExecutor()
semaphore = asyncio.Semaphore(5)
lock = asyncio.Lock()
total_urls = 0
complete_urls = 0


async def read_file(file_path: str) -> AsyncGenerator[str, None]:
    global total_urls
    async with aiofiles.open(file_path, "r") as file:
        async for line in file:
            total_urls += 1
            yield line.strip()


async def create_request(url: str, session: aiohttp.ClientSession) -> None:
    global complete_urls
    async with semaphore:
        retries = 3
        for _ in range(retries):
            try:
                async with session.get(
                    url, timeout=300
                ) as response:  # большой таймаут для тяжелых урлов
                    response.raise_for_status()  # выбрасывает ошибку если не 2xx

                    text_content = await response.text()

                    # используем дополнительный процесс для работы с json
                    loop = asyncio.get_running_loop()
                    json_str = await loop.run_in_executor(
                        executor, get_json_str, url, text_content
                    )

                    await write_to_file(
                        json_str
                    )  # сразу пишу в файл, чтобы не нагружать память
                    async with lock:
                        complete_urls += 1
                    return

            except aiohttp.ClientConnectorError as e:
                logging.warning(f"Connection error for {url}: {e}")
            except aiohttp.ServerTimeoutError as e:
                logging.warning(f"Timeout while fetching {url}: {e}")
            except aiohttp.ClientResponseError as e:
                logging.error(f"Invalid response from {url}: {e.status} {e.message}")
                async with lock:
                    complete_urls += 1
                return
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode JSON from {url}: {e}")
                async with lock:
                    complete_urls += 1
                return
            except aiohttp.ClientError as e:
                logging.warning(f"General client error for {url}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error for {url}: {e}", exc_info=True)
                async with lock:
                    complete_urls += 1
                return

            await asyncio.sleep(5)

        logging.error(f"[{url}] Failed after {retries} attempts")
        async with lock:
            complete_urls += 1


def get_json_str(url: str, text_content: str) -> str:  # функция для отдельного потока
    content = json.loads(text_content)
    json_str = json.dumps({"url": url, "content": content}, ensure_ascii=False)
    return json_str


async def write_to_file(json_str: str) -> None:
    async with aiofiles.open(OUTPUT_FILE, "a") as file:
        await file.write(f"{json_str}\n")


async def fetch_urls(file_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async for url in read_file(file_path):
            asyncio.create_task(create_request(url, session))

        while total_urls != complete_urls:  # чтобы успеть выйти из сессии
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    file = "./urls.txt"
    asyncio.run(fetch_urls(file))
