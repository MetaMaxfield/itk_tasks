import csv
import multiprocessing
import random
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime

from tabulate import tabulate

CPU_COUNT = multiprocessing.cpu_count()
VARS_TITLE = "Variants"
TIME_TITLE = "Time"

table_data = [
    [VARS_TITLE, TIME_TITLE],
]


@contextmanager
def timer(runner_type):
    start_time = datetime.now()
    yield
    end_time = datetime.now()

    table_data.append([runner_type, str(end_time - start_time)])


def data_collection(n: int):
    nums = []
    for _ in range(n):
        nums.append(random.randrange(1, 1001))
    return nums


def data_processing(number: int):
    """Factorial."""
    result = 1
    for num in range(1, number + 1):
        result *= num


def run_one_thread_one_process(nums):
    """Base var."""
    with timer("Base var"):
        for n in nums:
            data_processing(n)


def run_pool_threads(nums):
    """«А» var."""
    with timer("«А» var"):
        # использую одинаковое количество потоков и процессов для наглядности
        with ThreadPoolExecutor(max_workers=CPU_COUNT) as executor:
            executor.map(data_processing, nums)


def run_pool_processes(nums):
    """«Б» var."""
    with timer("«Б» var"):
        with multiprocessing.Pool(processes=CPU_COUNT) as pool:
            pool.map(data_processing, nums)


def run_processes_and_queues(nums):
    """«С» var."""

    def worker(q):
        while True:
            n = q.get()
            if n is None:
                break
            data_processing(n)

    def producer(q, ns):
        for n in ns:
            q.put(n)
        for _ in range(CPU_COUNT):  # флаги для остановки выделенных процессов
            q.put(None)

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


def print_tab():
    # использовал сторонний пакет, т.к. не нравились свои реализации...
    # ...(да и просто быстрее сделать так)
    tab = tabulate(table_data[1:], headers=table_data[0], tablefmt="github")
    print(tab)


def create_csv_file():
    file_name = "tab.csv"
    with open(file_name, "w") as file:
        writer = csv.writer(file)
        writer.writerows(table_data)
    print(f'\nCreated "{file_name}" with variants run times data.')


def main():
    nums = data_collection(1000000)

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
