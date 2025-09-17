# Вариант для экономии памяти
def two_sum(nums: list[int], target: int) -> tuple[int, int]:
    i1 = 0
    while i1 != len(nums) - 1:
        for i2 in range(i1 + 1, len(nums)):
            if nums[i1] + nums[i2] == target:
                return i1, i2
        i1 += 1


# Возможно более быстрый вариант
def two_sum2(nums: list[int], target: int) -> tuple[int, int]:
    memory_nums = {}
    for i, current_num in enumerate(nums):
        expected_num = target - current_num
        if expected_num in memory_nums:
            return i, memory_nums[expected_num]
        memory_nums[current_num] = i


if __name__ == "__main__":
    print("Var1:", two_sum([2, 7, 11, 15], 9))
    print("Var2:", two_sum2([2, 7, 11, 15], 9))
