import csv
import multiprocessing
import random
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

from tabulate import tabulate

CPU_COUNT = multiprocessing.cpu_count()
VARS_TITLE = "Variants"
TIME_TITLE = "Time"

table_data = [
    [VARS_TITLE, TIME_TITLE],
]


@contextmanager
def timer(runner_type: str) -> Generator[None, None, None]:
    start_time = datetime.now()
    yield
    end_time = datetime.now()

    table_data.append([runner_type, str(end_time - start_time)])


def data_collection(numbers: int) -> list[int]:
    nums = []
    for _ in range(numbers):
        nums.append(random.randrange(1, 1001))
    return nums


def data_processing(number: int) -> None:
    """Factorial."""
    result = 1
    for num in range(1, number + 1):
        result *= num


def run_one_thread_one_process(nums: list[int]) -> None:
    """Base var."""
    with timer("Base var"):
        for num in nums:
            data_processing(num)


def run_pool_threads(nums: list[int]) -> None:
    """«А» var."""
    with timer("«А» var"):
        # использую одинаковое количество потоков и процессов для наглядности
        with ThreadPoolExecutor(max_workers=CPU_COUNT) as executor:
            executor.map(data_processing, nums)


def run_pool_processes(nums: list[int]) -> None:
    """«Б» var."""
    with timer("«Б» var"):
        with multiprocessing.Pool(processes=CPU_COUNT) as pool:
            pool.map(data_processing, nums)


def run_processes_and_queues(nums: list[int]) -> None:
    """«С» var."""

    def worker(task_queue: multiprocessing.Queue) -> None:
        while True:
            number = task_queue.get()
            if number is None:
                break
            data_processing(number)

    def producer(task_queue: multiprocessing.Queue, numbers: list[int]) -> None:
        for number in numbers:
            task_queue.put(number)
        for _ in range(CPU_COUNT):  # флаги для остановки выделенных процессов
            task_queue.put(None)

    with timer("«С» var"):
        queue = multiprocessing.Queue()

        processes = []
        for _ in range(CPU_COUNT):
            process = multiprocessing.Process(target=worker, args=(queue,))
            processes.append(process)

        for process in processes:
            process.start()

        producer(queue, nums)

        for process in processes:
            process.join()


def print_tab() -> None:
    # использовал сторонний пакет, т.к. не нравились свои реализации...
    # ...(да и просто быстрее сделать так)
    tab = tabulate(table_data[1:], headers=table_data[0], tablefmt="github")
    print(tab)


def create_csv_file() -> None:
    file_name = "tab.csv"
    file_path = Path(__file__).resolve().parent / file_name
    with open(file_path, "w") as file:
        writer = csv.writer(file)
        writer.writerows(table_data)
    print(f'\nCreated "{file_name}" with variants run times data.')


def main() -> None:
    nums = data_collection(10)

    runners = [
        run_one_thread_one_process,
        run_pool_threads,
        run_pool_processes,
        run_processes_and_queues,
    ]
    for runner in runners:
        runner(nums)

    print_tab()

    create_csv_file()


if __name__ == "__main__":
    main()
